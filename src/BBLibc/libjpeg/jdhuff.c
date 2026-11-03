#include "jpeglib.h"


/*
* Module:                 BBLibc.dll
* Entry point:            0x10016730
*/

void jpeg_make_d_derived_tbl(j_decompress_ptr cinfo, boolean isDC, int tblno, d_derived_tbl **pdtbl)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10016BF7
*/

boolean jpeg_fill_bit_buffer(bitread_working_state *state, bit_buf_type get_buffer, int bits_left, int nbits)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10016DB2
*/

int jpeg_huff_decode(bitread_working_state *state, bit_buf_type get_buffer, int bits_left, d_derived_tbl *htbl, int min_bits)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10016F06
*/

void jinit_huff_decoder(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10016F7E
*/

static void start_pass_huff_decoder(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10017160
*/

static boolean decode_mcu(j_decompress_ptr cinfo, JBLOCKROW *MCU_data)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10017795
*/

static boolean process_restart(j_decompress_ptr cinfo)
{
}
