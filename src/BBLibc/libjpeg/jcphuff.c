#include "jpeglib.h"

struct phuff_entropy_encoder;
typedef struct phuff_entropy_encoder * phuff_entropy_ptr;


/*
* Module:                 BBLibc.dll
* Entry point:            0x10010620
*/

void jinit_phuff_encoder(j_compress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10010695
*/

static void start_pass_phuff(j_compress_ptr cinfo, boolean gather_statistics)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100108CB
*/

static boolean encode_mcu_DC_first(j_compress_ptr cinfo, JBLOCKROW *MCU_data)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10010AB0
*/

static void emit_bits(phuff_entropy_ptr entropy, unsigned int code, int size)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10010C02
*/

static void dump_buffer(phuff_entropy_ptr entropy)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10010C69
*/

static void emit_symbol(phuff_entropy_ptr entropy, int tbl_no, int symbol)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10010CD3
*/

static void emit_restart(phuff_entropy_ptr entropy, int restart_num)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10010DDB
*/

static void flush_bits(phuff_entropy_ptr entropy)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10010E04
*/

static void emit_eobrun(phuff_entropy_ptr entropy)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10010ED2
*/

static void emit_buffered_bits(phuff_entropy_ptr entropy, char *bufstart, unsigned int nbits)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10010F14
*/

static boolean encode_mcu_AC_first(j_compress_ptr cinfo, JBLOCKROW *MCU_data)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001117B
*/

static boolean encode_mcu_DC_refine(j_compress_ptr cinfo, JBLOCKROW *MCU_data)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100112A0
*/

static boolean encode_mcu_AC_refine(j_compress_ptr cinfo, JBLOCKROW *MCU_data)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10011641
*/

static void finish_pass_phuff(j_compress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100116A7
*/

static void finish_pass_gather_phuff(j_compress_ptr cinfo)
{
}
