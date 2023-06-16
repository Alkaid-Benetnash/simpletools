#include <vector>
#include <iostream>
#include <cassert>

#include "heap.hpp"

struct CpuNTasksLBEntry {
  int cpuid;
  size_t ntasks;
	// priorities when performing load balancing. The higher prio according to this
	// operator<, the fewer ntasks it has.
  bool operator<(const CpuNTasksLBEntry &other) const {
	  return this->ntasks > other.ntasks;
  }
  friend std::ostream& operator<<(std::ostream &os, const CpuNTasksLBEntry &e);
};
std::ostream& operator<<(std::ostream& os, const CpuNTasksLBEntry &e) {
  os << "[cpuid=" << e.cpuid << ", ntasks=" << e.ntasks << "]";
  return os;
}

typedef CpuNTasksLBEntry TestingType;
int main() {
  std::vector<TestingType> heap_orig = {
    {1, 10}, // 0
    {2, 40}, // 1
    {3, 15}, // 2
    {4, 2},  // 3
    {5, 10}, // 4
    {6, 12}, // 5
  };
  {
	std::cout << "heapsort without update" << std::endl;
    auto heap(heap_orig);
    std::make_heap(heap.begin(), heap.end());
	heaphelper::print(std::cout, heap);
  }

  {
	std::cout << "heapsort with update (one siftDown, one siftUp)" << std::endl;
    auto heap(heap_orig);
    std::make_heap(heap.begin(), heap.end());
	auto it = heap.begin() + 2; // [3, 15] -> [3, 9]
	heaphelper::update(heap.begin(), heap.end(), it, {it->cpuid,9});
    it = heap.begin() + 1; // [4, 2] -> [4, 12]
	heaphelper::update(heap.begin(), heap.end(), it, {it->cpuid, 20});
	std::vector<TestingType> sorted_results;
	sorted_results.reserve(heap.size());
	heaphelper::foreach_sorted(heap, [&](auto ref){
			sorted_results.push_back(ref);
			std::cout << ref << std::endl;
	});
	assert(std::is_sorted(sorted_results.rbegin(), sorted_results.rend()));
  }
  return 0;
}
