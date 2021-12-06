import gzip
import math

# Block size
# Associativity
# Allocate policy?
# Cache size
# Miss penalty

# 1) Total instructions                     <Instructions with +1 for reads or writes>
# 2) Total cycles                           <Instructions + Miss penalties>
# 3) Total CPU time (execution time)        <Calculated from total Cycles and Hz>
# 4) Memory accesses                        <sum of reads and writes>
# 5) Overall miss rate                      <recorded # of read and write misses>/<read count + write count>
# 6) Read miss rate                         <recorded # of read misses>/<read count>
# 7) Memory CPI                             <>
# 8) Total CPI                              <Total clocks/Total Instructions>
# 9) Average memory access time in cycles   <>
# 10) (read or write) Dirty evictions       <recorded # of evictions>
# 11) Load (read) misses                    <recorded # of read misses>
# 12) Store (write) misses                  <recorded # of write misses>
# 13) Load (read) hits                      <recorded # of read hits>
# 14) Store (read) Hits                     <recorded # of write hits>

# List[
#
# [ _  _  _  _ ]
# [            ]
# ...
#
# ]

# LRU [
#
# [ [D, T]  [D, T] ]
# [                ]
# ...
#
# ]

# Index gives set # (current set)
# Tag gives entry in set
# Offset subdivides a memory block



class Cache:
    def __init__(self, block_size = 16, associativity = 1, cache_size = 16, miss_penalty = 30):
        #Body of constructor
        self.block_size = block_size
        self.associativity = associativity
        self.cache_size = cache_size
        self.miss_penalty = miss_penalty
        self.offset_size = math.log(block_size, 2)
        self.num_sets = int((cache_size*1024)/(block_size*associativity))
        self.index_size = math.log(self.num_sets, 2)
        self.tag_size = 32 - self.offset_size - self.index_size
        self.total_cycles = 0
        self.instructions = 0
        self.dirty_evicts = 0
        self.read_misses = 0
        self.read_hits = 0
        self.write_misses = 0
        self.write_hits = 0

        self.cache = []
        for i in range(0, self.num_sets):
            cache_set = []
            for j in range(0, self.associativity):
                cache_set.append([0, 0])
            self.cache.append(cache_set)

    def parse_addr(self, addr_str):
        addr = int(addr_str, 16)
        return addr

    def read(self, read_tag, read_index, ic):
        #TODO: Implement read logic
        # check index for tag #
        # At index:
        # <hit> or <miss>
        # If <hit> no penalty
        #       - Increment by 1
        # If tag does not exist, is LRU clean or dirty?
        #   If clean <clean read miss>
        #       -Standard penalty
        #       -<store tag>
        #       -update the LRU order
        #           -delete tag
        #           -append tag <clean>
        #   If dirty <dirty read miss>
        #       -Dirty penalty
        #       -<store new tag in LRU>
        #       -update the LRU order
        #           -delete tag
        #           -append tag <clean>

        self.total_cycles = self.total_cycles + int(ic)
        # print(self.total_cycles)
        self.instructions = self.instructions + int(ic)

        assoc_list = self.cache[read_index]
        # Iterate over associations
        for i in range(0, len(assoc_list)):
            assoc = assoc_list[i]

            if read_tag == assoc[1]:
                # print('Its a Hit!')
                self.read_hits = self.read_hits + 1
                read_lru = assoc_list.pop(i)
                assoc_list.append(read_lru)
                return

        read_lru = assoc_list.pop(0)
        self.total_cycles = self.total_cycles + self.miss_penalty
        if read_lru[0] == 0:
            # print("The Miss is clean")
            self.read_misses = self.read_misses + 1
            assoc_list.append([0, read_tag])
            return

        elif read_lru[0] == 1:
            # print("The read Miss is dirty")
            self.total_cycles = self.total_cycles + 2
            self.dirty_evicts = self.dirty_evicts + 1
            self.read_misses = self.read_misses + 1
            assoc_list.append([0, read_tag])
            return
        return None

    def write(self, write_tag, write_index, ic):
        #TODO: Implement write logic
        # check index for tag #
        # At index:
        # <hit> or <miss>
        # If <hit> no penalty
        #       - Increment by 1
        # If tag does not exist, is LRU clean or dirty?
        #   If clean <clean write miss>
        #       -Standard penalty
        #       -<store tag>
        #       -update the LRU order
        #           -delete tag
        #           -append tag <dirty>
        #   If dirty <dirty write miss>
        #       -Dirty penalty
        #       -<store new tag in LRU>
        #       -update the LRU order
        #           -delete tag
        #           -append tag <dirty>

        self.total_cycles = self.total_cycles + int(ic)
        self.instructions = self.instructions + int(ic)

        assoc_list = self.cache[write_index]
        # Iterate over associations

        for i in range(0, len(assoc_list)):
            assoc = assoc_list[i]

            if write_tag == assoc[1]:
                # print('Its a Hit!')
                self.write_hits = self.write_hits + 1
                write_lru = assoc_list.pop(i)
                assoc_list.append([1, write_tag])
                return

        # print('Its a Miss!')
        write_lru = assoc_list.pop(0)
        self.total_cycles = self.total_cycles + self.miss_penalty
        if write_lru[0] == 0:
            # print("The Miss is clean")
            self.write_misses = self.write_misses + 1
            assoc_list.append([1, write_tag])
            return

        elif write_lru[0] == 1:
            # print("The write Miss is dirty")
            self.total_cycles = self.total_cycles + 2
            self.dirty_evicts = self.dirty_evicts + 1
            self.write_misses = self.write_misses + 1
            assoc_list.append([1, write_tag])
            return

        return None


if __name__ == "__main__":

    cache = Cache()
    with gzip.open('art.trace.gz', 'rb') as file:
        file_content = file.read().splitlines()

    for i in file_content:

            str_data = i.decode().split(" ")

            main_tag = cache.parse_addr(str_data[2]) >> (int(cache.offset_size + cache.index_size))
            main_temp = cache.parse_addr((str_data[2])) >> (int(cache.offset_size))
            mask = (1 << int(cache.index_size)) - 1
            main_index = main_temp & mask
            main_ic = int(str_data[3])

            if int(cache.parse_addr(str_data[1])) == 0:
                cache.read(main_tag, main_index, main_ic)

            if int(cache.parse_addr(str_data[1])) == 1:
                cache.write(main_tag, main_index, main_ic)



    print("Total Cycles:", int(cache.total_cycles))
    # print("Total Cycles:", cache.instructions + (cache.dirty_evicts * 2) + (
    #             (cache.read_misses + cache.write_misses) * cache.miss_penalty))
    print("Instructions:", int(cache.instructions))
    print("Dirty Evictions:", int(cache.dirty_evicts))
    print("Read Misses:", int(cache.read_misses))
    print("Read Hits:", int(cache.read_hits))
    print("Write Misses:", int(cache.write_misses))
    print("Write Hits:", int(cache.write_hits))
    print("Memory Accesses:", cache.read_hits + cache.read_misses + cache.write_misses + cache.write_hits)
    print("CPI:", (cache.instructions + (cache.dirty_evicts * 2) + (
                (cache.read_misses + cache.write_misses) * cache.miss_penalty))/cache.instructions)

    print("Average mem access in cycles:", ((cache.read_misses + cache.write_misses) * cache.miss_penalty + 2 * cache.dirty_evicts) / (
              cache.read_hits + cache.read_misses + cache.write_misses + cache.write_hits))
    print("Mem CPI:", ((cache.read_misses + cache.write_misses) * cache.miss_penalty + 2 * cache.dirty_evicts) /cache.instructions)

    print("Overall Miss Rate:", (cache.read_misses + cache.write_misses) /
          (cache.read_hits + cache.read_misses + cache.write_misses + cache.write_hits))

    print("Read Miss Rate:", (cache.read_misses)/(cache.read_hits + cache.read_misses))

    # Diagnostic print statements:
            #
            # print(str_data)
            # print(cache.parse_addr(str_data[2]))                                                # Full address
            # print(cache.parse_addr(str_data[2]) >> (int(cache.offset_size + cache.index_size))) # tag
            # temp = cache.parse_addr((str_data[2])) >> (int(cache.offset_size))
            # print(temp)                                                                         # Index and Tag
            # mask = (1 << int(cache.index_size)) - 1
            # print(mask)
            # index = temp & mask
            # print(index) # Just Index