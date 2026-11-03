#include "jpeglib.h"


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000F6D0
*/

void jpeg_add_quant_table(j_compress_ptr cinfo, int which_tbl, const unsigned int *basic_table, int scale_factor, boolean force_baseline)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000F7ED
*/

void jpeg_set_linear_quality(j_compress_ptr cinfo, int scale_factor, boolean force_baseline)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000F828
*/

int jpeg_quality_scaling(int quality)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000F86D
*/

void jpeg_set_quality(j_compress_ptr cinfo, int quality, boolean force_baseline)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000F895
*/

void jpeg_set_defaults(j_compress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000FA22
*/

static void std_huff_tables(j_compress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000FA9B
*/

static void add_huff_table(j_compress_ptr cinfo, JHUFF_TBL **htblptr, const UINT8 *bits, const UINT8 *val)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000FB6A
*/

void jpeg_default_colorspace(j_compress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1000FC1D
*/

void jpeg_set_colorspace(j_compress_ptr cinfo, J_COLOR_SPACE colorspace)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10010226
*/

void jpeg_simple_progression(j_compress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100104D2
*/

static jpeg_scan_info *fill_a_scan(jpeg_scan_info *scanptr, int ci, int Ss, int Se, int Ah, int Al)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10010519
*/

static jpeg_scan_info *fill_scans(jpeg_scan_info *scanptr, int ncomps, int Ss, int Se, int Ah, int Al)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001057F
*/

static jpeg_scan_info *fill_dc_scans(jpeg_scan_info *scanptr, int ncomps, int Ah, int Al)
{
}
