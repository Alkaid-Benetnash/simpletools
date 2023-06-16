#include <cassert>
#include <iostream>

#include "bithacks.hpp"
using namespace bithacks;

int main() {
  for (int i = 0; i < 32; ++i) {
    uint32_t power = 1U << i;
    uint32_t index = powerof2_index(static_cast<uint32_t>(power));
    if (index != i) {
      std::cout << "uint32_t powerof2_index(" << power << ") == " << index <<
        ", expected: " << i << " ?" << std::endl;
      abort();
    }
  }
  for (int i = 0; i < 64; ++i) {
    uint64_t power = 1UL << i;
    uint32_t index = powerof2_index(static_cast<uint64_t>(power));
    if (index != i) {
      std::cout << "uint64_t powerof2_index(" << power << ") == " << index <<
        ", expected: " << i << " ?" << std::endl;
    }
  }
  return 0;
}
