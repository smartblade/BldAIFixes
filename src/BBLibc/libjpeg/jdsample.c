#include "jpeglib.h"


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001EA30
*/

void jinit_upsampler(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001ED04
*/

static void start_pass_upsample(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001ED33
*/

static void sep_upsample(j_decompress_ptr cinfo, JSAMPIMAGE input_buf, JDIMENSION *in_row_group_ctr, JDIMENSION in_row_groups_avail, JSAMPARRAY output_buf, JDIMENSION *out_row_ctr, JDIMENSION out_rows_avail)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001EE8E
*/

static void fullsize_upsample(j_decompress_ptr cinfo, jpeg_component_info *compptr, JSAMPARRAY input_data, JSAMPARRAY *output_data_ptr)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001EE9B
*/

static void noop_upsample(j_decompress_ptr cinfo, jpeg_component_info *compptr, JSAMPARRAY input_data, JSAMPARRAY *output_data_ptr)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001EEA9
*/

static void int_upsample(j_decompress_ptr cinfo, jpeg_component_info *compptr, JSAMPARRAY input_data, JSAMPARRAY *output_data_ptr)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001EFBF
*/

static void h2v1_upsample(j_decompress_ptr cinfo, jpeg_component_info *compptr, JSAMPARRAY input_data, JSAMPARRAY *output_data_ptr)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001F054
*/

static void h2v2_upsample(j_decompress_ptr cinfo, jpeg_component_info *compptr, JSAMPARRAY input_data, JSAMPARRAY *output_data_ptr)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001F121
*/

static void h2v1_fancy_upsample(j_decompress_ptr cinfo, jpeg_component_info *compptr, JSAMPARRAY input_data, JSAMPARRAY *output_data_ptr)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1001F26C
*/

static void h2v2_fancy_upsample(j_decompress_ptr cinfo, jpeg_component_info *compptr, JSAMPARRAY input_data, JSAMPARRAY *output_data_ptr)
{
}
