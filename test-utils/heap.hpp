#include <iterator>
#include <ostream>
#include <algorithm>
#include <functional>

/*
 * heaphelper functions are extensions to the std::make_heap related heap
 * datastructure.
 *
 */
namespace heaphelper {

/* `update`: update an element in a heapified, random-accessible containers.
 * Will perform siftUp and siftDown operations if necessary.
 */
template < class RandomIt,
           class Compare = std::less<typename RandomIt::value_type> >
void update(
    RandomIt begin, RandomIt end, RandomIt item_it,
    typename std::iterator_traits<RandomIt>::value_type new_val,
    Compare compLT = Compare{}) {
  // assumption this is for a maxheap
  typename std::iterator_traits<RandomIt>::value_type old_val = *item_it;
  auto size = end - begin;
  // std::cout << "data structure size=" <<  size << std::endl;
  // std::cout << ">>>> Updating from " << old_val << std::endl;
  // std::cout << "<<<<          to   " << new_val << std::endl;
  *item_it = new_val;
  if (compLT(old_val, new_val)) {
    // old_val < new_val, siftUp
    while (item_it != begin) {
      auto offset = item_it - begin;
      RandomIt parent_it = begin + (offset - 1) / 2;
      if (compLT(*parent_it, *item_it)) {
        // parent < item
        std::iter_swap(parent_it, item_it);
        item_it = parent_it;
      } else {
        // parent >= item
        break;
      }
    }
  } else {
    // old_val >= new_val, siftDown
    while (true) {
      auto offset = item_it - begin;
      auto childL_off = (offset * 2) + 1;
      auto childR_off = (offset * 2) + 2;
      RandomIt childL_it = begin + (offset * 2) + 1;
      RandomIt childR_it = begin + (offset * 2) + 2;
      RandomIt max_child_it = childL_it;
      if (childL_off >= size)
        break;
      if (childR_off < size && compLT(*childL_it, *childR_it)) {
        max_child_it = childR_it;
      }
      if (compLT(*item_it, *max_child_it)) {
        // item < child
        std::iter_swap(item_it, max_child_it);
        item_it = max_child_it;
      } else {
        // item >= child
        break;
      }
    }
  }
}

template <class Container>
void foreach_sorted(Container &heap,
    std::function<void(typename Container::const_reference)> op) {
  while (!heap.empty()) {
    std::pop_heap(heap.begin(), heap.end());
    typename Container::const_reference e = heap.back();
    op(e);
    heap.pop_back();
  }
}

template <class Container>
void print(std::ostream &os, Container &heap) {
  foreach_sorted(heap, [&os](typename Container::const_reference e) {
      os << e << std::endl;
  });
}

} // namespace heaphelper
