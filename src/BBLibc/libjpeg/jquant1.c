#include "jpeglib.h"

/* int (*ODITHER_MATRIX_PTR)[ODITHER_SIZE] */
typedef int * ODITHER_MATRIX_PTR;


/*
* Module:                 BBLibc.dll
* Entry point:            0x10023A30
*/

void jinit_1pass_quantizer(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10023B19
*/

static void create_colormap(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10023CDA
*/

static int select_ncolors(j_decompress_ptr cinfo, int *Ncolors)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10023E52
*/

static int output_value(j_decompress_ptr cinfo, int ci, int j, int maxj)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10023E6E
*/

static void create_colorindex(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10024015
*/

static int largest_input_value(j_decompress_ptr cinfo, int ci, int j, int maxj)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10024032
*/

static void alloc_fs_workspace(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10024094
*/

static void start_pass_1_quant(j_decompress_ptr cinfo, boolean is_pre_scan)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100241EA
*/

static void create_odither_tables(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10024296
*/

static ODITHER_MATRIX_PTR make_odither_array(j_decompress_ptr cinfo, int ncolors)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10024357
*/

static void color_quantize(j_decompress_ptr cinfo, JSAMPARRAY input_buf, JSAMPARRAY output_buf, int num_rows)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10024436
*/

static void color_quantize3(j_decompress_ptr cinfo, JSAMPARRAY input_buf, JSAMPARRAY output_buf, int num_rows)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10024538
*/

static void quantize_ord_dither(j_decompress_ptr cinfo, JSAMPARRAY input_buf, JSAMPARRAY output_buf, int num_rows)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10024677
*/

static void quantize3_ord_dither(j_decompress_ptr cinfo, JSAMPARRAY input_buf, JSAMPARRAY output_buf, int num_rows)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100247FF
*/

static void quantize_fs_dither(j_decompress_ptr cinfo, JSAMPARRAY input_buf, JSAMPARRAY output_buf, int num_rows)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10024A44
*/

static void finish_pass_1_quant(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10024A49
*/

static void new_color_map_1_quant(j_decompress_ptr cinfo)
{
}
