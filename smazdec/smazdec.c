
#include <stdbool.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include <arpa/inet.h>

static void usage(const char *arg0) {
  printf(
    "Usage: %s INPUT_FILE [OUTPUT_FILE]\n"
    "  INPUT_FILE   The file to decode\n"
    "  OUTPUT_FILE  The file to write out, or stdout if no file is specified\n\n",
    arg0);
}

static bool find_sync(FILE *f) {
  int sync_length = 0, c;

  while ((c = fgetc(f)) != EOF) {
    switch (sync_length) {
      case 0: sync_length = (c == 'S') ? 1 : 0; break;
      case 1: sync_length = (c == 'M') ? 2 : 0; break;
      case 2: sync_length = (c == 'A') ? 3 : 0; break;
      case 3:
        if (c == 'Z')
          return true;
        else
          sync_length = 0;
        break;
    }
  }

  return false;
}

#define SAFE
#if defined(SAFE)
# if defined(__DEBUG__)
#  define fail(x,r)   if (x) { printf("%s #%d\n", __FILE__, __LINE__); *dst_len = olen; return r; }
# else
#  define fail(x,r)   if (x) { *dst_len = olen; return r; }
# endif // __DEBUG__
#else
# define fail(x,r)
#endif // SAFE

/* Thinned out version of the UCL 2e decompression sourcecode
 * Original (C) Markus F.X.J Oberhumer under GNU GPL license */

#define GETBYTE(src)  (src[ilen++])

#define GETBIT(bb, src) \
    (((bb = ((bb & 0x7f) ? (bb*2) : ((unsigned)GETBYTE(src)*2+1))) >> 8) & 1)

enum status {
    UCL_E_OK                =  0,
    UCL_E_INPUT_OVERRUN     = -0x1,
    UCL_E_OUTPUT_OVERRUN    = -0x2,
    UCL_E_LOOKBEHIND_OVERRUN= -0x3,
    UCL_E_OVERLAP_OVERRUN   = -0x4,
    UCL_E_INPUT_NOT_CONSUMED= -0x5
};

static enum status decompress(const unsigned char* src, unsigned int src_len,
    unsigned char* dst, unsigned int* dst_len) {
  unsigned int bb = 0;
  unsigned int ilen = 0, olen = 0, last_m_off = 1;

#if defined(SAFE)
  const unsigned int oend = *dst_len;
#endif

  for (;;) {
    unsigned int m_off, m_len;

    while (GETBIT(bb,src)) {
      fail(ilen >= src_len, UCL_E_INPUT_OVERRUN);
      fail(olen >= oend, UCL_E_OUTPUT_OVERRUN);
      dst[olen++] = GETBYTE(src);
    }

    m_off = 1;

    for (;;) {
      m_off = m_off*2 + GETBIT(bb,src);
      fail(ilen >= src_len, UCL_E_INPUT_OVERRUN);
      fail(m_off > 0xfffffful + 3, UCL_E_LOOKBEHIND_OVERRUN);
      if (GETBIT(bb,src)) {
        break;
      }
      m_off = (m_off-1)*2 + GETBIT(bb,src);
    }

    if (m_off == 2) {
      m_off = last_m_off;
      m_len = GETBIT(bb,src);
    } else {
      fail(ilen >= src_len, UCL_E_INPUT_OVERRUN);
      m_off = (m_off-3)*256 + GETBYTE(src);
      if (m_off == 0xfffffffful) {
        break;
      }
      m_len = (m_off ^ 0xfffffffful) & 1;
      m_off >>= 1;
      last_m_off = ++m_off;
    }

    if (m_len) {
      m_len = 1 + GETBIT(bb,src);
    } else if (GETBIT(bb,src)) {
      m_len = 3 + GETBIT(bb,src);
    } else {
      m_len++;
      do {
        m_len = m_len*2 + GETBIT(bb,src);
        fail(ilen >= src_len, UCL_E_INPUT_OVERRUN);
        fail(m_len >= oend, UCL_E_OUTPUT_OVERRUN);
      } while (!GETBIT(bb,src));
      m_len += 3;
    }

    m_len += (m_off > 0x500);
    fail(olen + m_len > oend, UCL_E_OUTPUT_OVERRUN);
    fail(m_off > olen, UCL_E_LOOKBEHIND_OVERRUN);

    {
      const unsigned char* m_pos;
      m_pos = dst + olen - m_off;
      dst[olen++] = *m_pos++;
      do {
        dst[olen++] = *m_pos++;
      } while (--m_len > 0);
    }
  }

  *dst_len = olen;

  return (ilen == src_len) ? UCL_E_OK : (ilen < src_len ? UCL_E_INPUT_NOT_CONSUMED : UCL_E_INPUT_OVERRUN);
}

int main(int argc, const char **argv) {
  FILE *in, *out;
  uint32_t read_word;
  uint8_t *packed_buffer = NULL, *unpacked_buffer = NULL;
  int ret = EXIT_FAILURE;

  if (argc != 2 && argc != 3) {
    usage(argv[0]);
    return EXIT_FAILURE;
  }

  if (argc == 2) {
    if (strcmp(argv[1], "-h") == 0 ||
      strcmp(argv[1], "--help") == 0) {
      usage(argv[0]);
      return EXIT_SUCCESS;
    }
  }

  do {
    /* Open the input file */
    in = fopen(argv[1], "r");
    if (!in) {
      fprintf(stderr, "Failed to open input file: %s\n", argv[1]);
      break;
    }

    /* Open the output file */
    out = (argc == 2) ? stderr : fopen(argv[2], "w");
    if (!out) {
      fprintf(stderr, "Failed to open output file: %s\n", argv[1]);
      break;
    }

    /* Find the SMAZ sync word */
    if (!find_sync(in)) {
      fputs("Failed to find SMAZ sync\n", stderr);
      break;
    }

    /* Read the pre-header */
    if (fseek(in, -12, SEEK_CUR) == -1) {
      fputs("Failed seeking to SMAZ pre-header\n", stderr);
      break;
    }

    if (fread(&read_word, sizeof(read_word), 1, in) != 1) {
      fputs("Failed to read CRC\n", stderr);
      break;
    }
    const uint32_t crc = htonl(read_word);
    (void)crc;  /* unused */

    if (fread(&read_word, sizeof(read_word), 1, in) != 1) {
      fputs("Failed to read unpacked length field\n", stderr);
      break;
    }
    const uint32_t unpacked_length = htonl(read_word);

    /* Read the header */
    if (fseek(in, 4, SEEK_CUR) == -1) {
      fputs("Failed seeking to SMAZ header\n", stderr);
      break;
    }

    if (fread(&read_word, sizeof(read_word), 1, in) != 1) {
      fputs("Failed to read SMAZ header\n", stderr);
      break;
    }
    const uint32_t max_packed_chunk_length = htonl(read_word);

    /* Allocate the buffers */
    packed_buffer = (uint8_t*)malloc(max_packed_chunk_length);
    if (!packed_buffer) {
      fprintf(stderr, "Failed to allocate buffer of %d bytes\n", max_packed_chunk_length);
      break;
    }

    unpacked_buffer = (uint8_t*)malloc(unpacked_length);
    if (!unpacked_buffer) {
      fprintf(stderr, "Failed to allocate buffer of %d bytes\n", unpacked_length);
      break;
    }

    /* Decode the chunks */
    uint32_t length = 0;
    while (length < unpacked_length) {
      if (fread(&read_word, sizeof(read_word), 1, in) != 1) {
        fputs("Failed to read the unpacked chunk length\n", stderr);
        break;
      }
      const uint32_t unpacked_chunk_length = htonl(read_word);

      if (fread(&read_word, sizeof(read_word), 1, in) != 1) {
        fputs("Failed to read the packed chunk length\n", stderr);
        break;
      }
      const uint32_t packed_chunk_length = htonl(read_word);

      if (packed_chunk_length > max_packed_chunk_length) {
        fprintf(stderr, "Warning: Chunk length of %d-bytes is longer than %d-bytes declared in header\n",
            packed_chunk_length, max_packed_chunk_length);
        packed_buffer = (uint8_t*)realloc(packed_buffer, packed_chunk_length);
      }

      if (packed_chunk_length != fread(packed_buffer, 1, packed_chunk_length, in)) {
        fprintf(stderr, "Failed to read %u-bytes of chunk data.", packed_chunk_length);
        break;
      }

      unsigned int decoded_length = unpacked_chunk_length;
      const enum status result = decompress(packed_buffer, packed_chunk_length, unpacked_buffer, &decoded_length);
      if (result != UCL_E_OK) {
        const char *reason;
        switch (result) {
          case UCL_E_INPUT_OVERRUN: reason = "Input over-run"; break;
          case UCL_E_OUTPUT_OVERRUN: reason = "Output over-run"; break;
          case UCL_E_LOOKBEHIND_OVERRUN: reason = "Look-behind over-run"; break;
          case UCL_E_OVERLAP_OVERRUN: reason = "Overlap over-run"; break;
          case UCL_E_INPUT_NOT_CONSUMED: reason = "Input not consumed"; break;
          default: reason = "Unknown"; break;
        }
        fprintf(stderr, "Failed to decode chunk: %s\n", reason);
        break;
      }

      if (decoded_length != unpacked_chunk_length) {
        fprintf(stderr, "Expected chunk length of %u-bytes. Got %u-bytes.\n", decoded_length, unpacked_chunk_length);
        break;
      }

      if (decoded_length != fwrite(unpacked_buffer, 1, decoded_length, out)) {
        fputs("Failed while writing out unpacked data", stderr);
        break;
      }

      length += decoded_length;
    }
  
    if (length == unpacked_length)
       ret = EXIT_SUCCESS;
  } while (0);

  if (packed_buffer)
    free(packed_buffer);
  if (unpacked_buffer)
    free(unpacked_buffer);
  if (in)
    fclose(in);
  if (out && out != stdout)
    fclose(out);

  return ret;
}

