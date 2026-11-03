#include "jpeglib.h"

struct box;
typedef struct box * boxptr;


/*
* Module:                 BBLibc.dll
* Entry point:            0x10024A70
*/

void jinit_2pass_quantizer(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10024C3A
*/

static void init_error_limit(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10024D38
*/

static void start_pass_2_quant(j_decompress_ptr cinfo, boolean is_pre_scan)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10024ED3
*/

static void prescan_quantize(j_decompress_ptr cinfo, JSAMPARRAY input_buf, JSAMPARRAY output_buf, int num_rows)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10024FA9
*/

static void pass2_no_dither(j_decompress_ptr cinfo, JSAMPARRAY input_buf, JSAMPARRAY output_buf, int num_rows)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100250C5
*/

static void fill_inverse_cmap(j_decompress_ptr cinfo, int c0, int c1, int c2)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100252A3
*/

static int find_nearby_colors(j_decompress_ptr cinfo, int minc0, int minc1, int minc2, JSAMPLE *colorlist)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100257D0
*/

static void find_best_colors(j_decompress_ptr cinfo, int minc0, int minc1, int minc2, int numcolors, JSAMPLE *colorlist, JSAMPLE *bestcolor)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10025A2F
*/

static void pass2_fs_dither(j_decompress_ptr cinfo, JSAMPARRAY input_buf, JSAMPARRAY output_buf, int num_rows)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10025E00
*/

static void finish_pass1(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10025E3A
*/

static void select_colors(j_decompress_ptr cinfo, int desired_colors)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10025F35
*/

static void update_box(j_decompress_ptr cinfo, boxptr boxp)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1002642C
*/

static int median_cut(j_decompress_ptr cinfo, boxptr boxlist, int numboxes, int desired_colors)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10026606
*/

static boxptr find_biggest_color_pop(boxptr boxlist, int numboxes)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1002666F
*/

static boxptr find_biggest_volume(boxptr boxlist, int numboxes)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100266CF
*/

static void compute_color(j_decompress_ptr cinfo, boxptr boxp, int icolor)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10026874
*/

static void finish_pass2(j_decompress_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10026879
*/

static void new_color_map_2_quant(j_decompress_ptr cinfo)
{
}
