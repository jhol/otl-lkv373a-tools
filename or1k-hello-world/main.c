
#include <stdio.h>
#include <sys/reent.h>

int __errno;
unsigned long _or1k_board_clk_freq = 0;

void _or1k_board_exit() {}

struct __siov {
  const void *iov_base;
  size_t iov_len;
};

struct __suio {
  struct __siov *uio_iov;
  int uio_iovcnt;
  size_t uio_resid;
};

typedef int (*__sfvwrite_r_func)(struct _reent*, void*, struct __suio *io);

void _or1k_outbyte(char c) {
  /* Borrow the implementation of newlib's __sfvwrite_r_func located in the main firmware. */
  char str[1] = {c};
  struct __siov iov = {str, 1};
  struct __suio uio = {&iov, 1, 1};
  struct _reent *r = *(struct _reent**)0x10161c;
  ((__sfvwrite_r_func)0xa512c)(r, r->_stdout, &uio);
}

void main(void) {
  printf(
      "\n"
      "-------------------------------------------------------------------\n"
      "  OOO  PPPP  EEEEE N   N TTTTT EEEEE  CCC  H   H L       A   BBBB  \n"
      " O   O P   P E     NN  N   T   E     C   C H   H L      A A  B   B \n"
      " O   O PPPP  EEEE  N N N   T   EEEE  C     HHHHH L     AAAAA BBBB  \n"
      " O   O P     E     N  NN   T   E     C   C H   H L     A   A B   B \n"
      "  OOO  P     EEEEE N   N   T   EEEEE  CCC  H   H LLLLL A   A BBBB  \n"
      "\n"
      "                  Hello World from printf(%d)\n"
      "-------------------------------------------------------------------\n"
      "\n",
      12345);
}
                                                                             
