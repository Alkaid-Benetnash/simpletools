// Compile: g++ --std=c++17 multithread.cpp
#include <sched.h>
#include <unistd.h>

#include <atomic>
#include <cassert>
#include <charconv>
#include <chrono>
#include <iostream>
#include <memory>
#include <mutex>
#include <string>
#include <string_view>
#include <thread>
#include <type_traits>
#include <unordered_map>
using namespace std;

class Worker {
 public:
  Worker(bool _busy_poll)
      : requested_print(false),
        requested_terminate(false),
        busy_poll(_busy_poll),
        t(&std::remove_pointer<decltype(this)>::type::run, this) {}

  ~Worker() {
    if (!requested_terminate) {
      request_terminate();
    }
    t.join();
  }

  void run() {
    std::cout << "New Thread created. ID: " << t.get_id() << ", native id "
              << t.native_handle() << ", tid " << gettid() << std::endl;
    while (true) {
      if (requested_terminate) {
        std::lock_guard<std::mutex> guard(worker_gmutex);
        std::cout << "Thread Terminated. ID: " << t.get_id() << ", native id "
                  << t.native_handle() << std::endl;
        return;
      }
      if (requested_print) {
        std::lock_guard<std::mutex> guard(worker_gmutex);
        cout << "Thread " << std::this_thread::get_id() << ", tid " << gettid()
             << ", running on " << sched_getcpu() << ", busy? " << busy_poll
             << endl;
        requested_print = false;
      }
      if (busy_poll)
        std::this_thread::yield();
      else
        std::this_thread::sleep_for(std::chrono::milliseconds(300));
    }
  }
  void request_print() { requested_print = true; }
  void request_terminate() { requested_terminate = true; }
  std::thread::native_handle_type get_native_tid() { return t.native_handle(); }

 private:
  static std::mutex worker_gmutex;
  bool busy_poll;
  std::atomic<bool> requested_print;
  std::atomic<bool> requested_terminate;
  std::thread t;
};
std::mutex Worker::worker_gmutex;

class WorkerManager {
 public:
   ~WorkerManager() {
     delAllThread();
   }
  void newThread(bool busy_poll) {
    std::unique_ptr<Worker> new_worker_up = std::make_unique<Worker>(busy_poll);
    workers.emplace(std::make_pair(new_worker_up->get_native_tid(),
                                   std::move(new_worker_up)));
  }

  void delThread(std::thread::native_handle_type native_tid) {
    auto find_it = workers.find(native_tid);
    if (find_it != workers.end()) {
      auto &worker = find_it->second;
      worker->request_terminate();
      workers.erase(find_it);
    }
  }

  void delAllThread() {
    for (auto &worker_entry : workers) {
      auto &worker = worker_entry.second;
      worker->request_terminate();
    }
    workers.clear();
  }

  void printAllThread() {
    for (auto &worker_entry : workers) {
      worker_entry.second->request_print();
    }
  }

 private:
  std::unordered_map<std::thread::native_handle_type, std::unique_ptr<Worker>>
      workers;
};

// TODO: use cpp argparse
std::string_view getopt_str(std::string_view to_parse, std::string_view option,
                            std::string_view default_value) {
  auto pos = to_parse.find(option);
  if (pos != std::string_view::npos) {
    // pos is updated to either a space or a non-space char immediately
    // following the option string
    pos += option.size();
    auto opt_val_start = (to_parse[pos] == ' ') ? pos + 1 : pos;
    auto opt_val_end = to_parse.find(' ', opt_val_start);
    return to_parse.substr(opt_val_start, opt_val_end);
  } else {
    return default_value;
  }
}

bool getopt_bool(std::string_view to_parse, std::string_view option,
                 bool default_value) {
  return to_parse.find(option) != std::string_view::npos;
}

/*
 * Create new worker threads
 * can take one optional option that means the number of threads to create
 * By default, create one thread
 * cmdline: new [-s] [-b] [-n $NTHREADS]
 */
void cmdProcessNew(WorkerManager &workermgr, std::string_view options) {
  bool busy_poll = false;  // default is sleep
  {                        // check the -b (busy sleep) or -s (sleep) flag
    bool is_busy = getopt_bool(options, "-b", false);
    if (is_busy) busy_poll = true;
    bool is_sleep = getopt_bool(options, "-s", false);
    if (is_sleep) busy_poll = false;
  }
  int nthreads;
  std::string_view nthreads_str = getopt_str(options, "-n", "1");

  auto [ptr, ec] = std::from_chars(
      nthreads_str.data(), nthreads_str.data() + nthreads_str.size(), nthreads);
  if (ec != std::errc()) {
    nthreads = 1;
  }
  for (auto i = 0; i < nthreads; i++) {
    workermgr.newThread(busy_poll);
  }
}

void cmdProcessDel(WorkerManager &workermgr, std::string_view options) {
  std::thread::native_handle_type native_id;
  auto [ptr, ec] = std::from_chars(options.data(),
                                   options.data() + options.size(), native_id);
  if (ec != std::errc()) {
    workermgr.delAllThread();
  } else {
    workermgr.delThread(
        static_cast<std::thread::native_handle_type>(native_id));
  }
}

void cmdProcessInfo(WorkerManager &workermgr, std::string_view options) {
  workermgr.printAllThread();
  std::this_thread::sleep_for(std::chrono::milliseconds(350));
}

int main() {
  WorkerManager workermgr;
  pid_t pid = getpid();
  std::cout << "Current pid: " << pid << std::endl;
  while (std::cin) {
    string line;
    cout << ">> Enter CMD: ";
    getline(cin, line);
    auto size = line.size();
    auto firstSpace = line.find(' ');
    if (size < 2) {
      continue;
    }
    std::string options = line.substr(firstSpace + 1);
    string cmd = line.substr(0, firstSpace);
    if (cmd == "new") {
      cmdProcessNew(workermgr, options);
    } else if (cmd == "del") {
      cmdProcessDel(workermgr, options);
    } else if (cmd == "info") {
      cmdProcessInfo(workermgr, options);
    } else if (cmd == "exit" || cmd == "quit") {
      break;
    } else {
      std::cout << "Invalid Commands. Ignored!" << std::endl;
    }
  }
  std::cout << "Exiting..." << std::endl;
  return 0;
}
