namespace bithacks {
// deBrujinLookupTables are generated using python script de_bruijn.py
constexpr uint8_t deBruijnLookupTable_uint64[64] = {
0, 1, 2, 7, 3, 13, 8, 19, 4, 25, 14, 28, 9, 34, 20, 40, 5, 17, 26, 38, 15, 46, 29, 48, 10, 31, 35, 54, 21, 50, 41, 57, 63, 6, 12, 18, 24, 27, 33, 39, 16, 37, 45, 47, 30, 53, 49, 56, 62, 11, 23, 32, 36, 44, 52, 55, 61, 22, 43, 51, 60, 42, 59, 58
};

inline uint8_t powerof2_index(uint64_t powerof2) {
        return deBruijnLookupTable_uint64[((0x218a392cd3d5dbf * powerof2) >> 58)];
}
constexpr uint8_t deBruijnLookupTable_uint32[32] = {
0, 1, 2, 6, 3, 11, 7, 16, 4, 14, 12, 21, 8, 23, 17, 26, 31, 5, 10, 15, 13, 20, 22, 25, 30, 9, 19, 24, 29, 18, 28, 27
};
inline uint8_t powerof2_index(uint32_t powerof2) {
        return deBruijnLookupTable_uint32[((0x4653adf * powerof2) >> 27)];
}
} // namespace bithacks
