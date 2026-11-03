#include "jpeglib.h"

struct working_state;


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000BD80
*/

void jpeg_make_c_derived_tbl(j_compress_ptr cinfo, boolean isDC, int tblno, c_derived_tbl **pdtbl)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000C0BE
*/

void jpeg_gen_optimal_table(j_compress_ptr cinfo, JHUFF_TBL *htbl, long *freq)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000C580
*/

void jinit_huff_encoder(j_compress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000C607
*/

static void start_pass_huff(j_compress_ptr cinfo, boolean gather_statistics)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000C80D
*/

static boolean encode_mcu_huff(j_compress_ptr cinfo, JBLOCKROW *MCU_data)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000C9AC
*/

static boolean encode_one_block(working_state *state, JCOEFPTR block, int last_dc_val, c_derived_tbl *dctbl, c_derived_tbl *actbl)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000CC15
*/

static boolean emit_bits(working_state *state, unsigned int code, int size)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000CD6C
*/

static boolean dump_buffer(working_state *state)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000CDB5
*/

static boolean emit_restart(working_state *state, int restart_num)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000CEA5
*/

static boolean flush_bits(working_state *state)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000CEDD
*/

static void finish_pass_huff(j_compress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000CF7A
*/

static boolean encode_mcu_gather(j_compress_ptr cinfo, JBLOCKROW *MCU_data)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000D08D
*/

static void htest_one_block(j_compress_ptr cinfo, JCOEFPTR block, int last_dc_val, long *dc_counts, long *ac_counts)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000D205
*/

static void finish_pass_gather(j_compress_ptr cinfo)
{
}
