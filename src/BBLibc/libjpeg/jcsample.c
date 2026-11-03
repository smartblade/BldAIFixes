#include "jpeglib.h"


/*
* Module:                 BBLibc.dll
* Entry point:            0x10011F30
*/

void jinit_downsampler(j_compress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10012153
*/

static void start_pass_downsample(j_compress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10012158
*/

static void sep_downsample(j_compress_ptr cinfo, JSAMPIMAGE input_buf, JDIMENSION in_row_index, JSAMPIMAGE output_buf, JDIMENSION out_row_group_index)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100121E7
*/

static void int_downsample(j_compress_ptr cinfo, jpeg_component_info *compptr, JSAMPARRAY input_data, JSAMPARRAY output_data)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10012353
*/

static void expand_right_edge(JSAMPARRAY image_data, int num_rows, JDIMENSION input_cols, JDIMENSION output_cols)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100123CA
*/

static void fullsize_downsample(j_compress_ptr cinfo, jpeg_component_info *compptr, JSAMPARRAY input_data, JSAMPARRAY output_data)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001241B
*/

static void h2v1_downsample(j_compress_ptr cinfo, jpeg_component_info *compptr, JSAMPARRAY input_data, JSAMPARRAY output_data)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100124E9
*/

static void h2v2_downsample(j_compress_ptr cinfo, jpeg_component_info *compptr, JSAMPARRAY input_data, JSAMPARRAY output_data)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100125F5
*/

static void h2v2_smooth_downsample(j_compress_ptr cinfo, jpeg_component_info *compptr, JSAMPARRAY input_data, JSAMPARRAY output_data)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100129B4
*/

static void fullsize_smooth_downsample(j_compress_ptr cinfo, jpeg_component_info *compptr, JSAMPARRAY input_data, JSAMPARRAY output_data)
{
}
