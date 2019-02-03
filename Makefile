CXXFLAGS=-msse4.2 -flto -O3 -pthread

crack-crc32: crack-crc32.o
	$(CXX) -o $@ $^ $(CXXFLAGS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -o $@ -c $<

clean:
	rm crack-crc32 *.o

.PHONY: clean
