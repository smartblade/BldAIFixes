#include "jpeglib.h"


/*
* Module:                 BBLibc.dll
* Entry point:            0x10018AA0
*/

boolean jpeg_resync_to_restart(j_decompress_ptr cinfo, int desired)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10018C16
*/

static boolean next_marker(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10018E36
*/

void jinit_marker_reader(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10018EEC
*/

static boolean get_interesting_appn(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10019118
*/

static void examine_app0(j_decompress_ptr cinfo, JOCTET *data, unsigned int datalen, INT32 remaining)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100194DC
*/

static void examine_app14(j_decompress_ptr cinfo, JOCTET *data, unsigned int datalen, INT32 remaining)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001962B
*/

static boolean skip_variable(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10019770
*/

static int read_markers(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10019BF8
*/

static boolean get_soi(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10019D0E
*/

static boolean get_sof(j_decompress_ptr cinfo, boolean is_prog, boolean is_arith)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001A32B
*/

static boolean get_sos(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001A86C
*/

static boolean get_dht(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001AF2C
*/

static boolean get_dqt(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001B3A6
*/

static boolean get_dri(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001B595
*/

static boolean first_marker(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001B6C6
*/

static boolean read_restart_marker(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001B79A
*/

static void reset_marker_reader(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001B7F7
*/

void jpeg_save_markers(j_decompress_ptr cinfo, int marker_code, unsigned int length_limit)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001B8FD
*/

static boolean save_marker(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001BCCC
*/

void jpeg_set_marker_processor(j_decompress_ptr cinfo, int marker_code, jpeg_marker_parser_method routine)
{
}
