#include "jpeglib.h"


/*
* Module:                 BBLibc.dll
* Entry point:            0x100225E0
*/

void jinit_memory_mgr(j_common_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100227DF
*/

static void *alloc_small(j_common_ptr cinfo, int pool_id, size_t sizeofobject)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100229A5
*/

static void out_of_memory(j_common_ptr cinfo, int which)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100229CF
*/

static void *alloc_large(j_common_ptr cinfo, int pool_id, size_t sizeofobject)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10022AC1
*/

static JSAMPARRAY alloc_sarray(j_common_ptr cinfo, int pool_id, JDIMENSION samplesperrow, JDIMENSION numrows)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10022BC2
*/

static JBLOCKARRAY alloc_barray(j_common_ptr cinfo, int pool_id, JDIMENSION blocksperrow, JDIMENSION numrows)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10022CD7
*/

static jvirt_sarray_ptr request_virt_sarray(j_common_ptr cinfo, int pool_id, boolean pre_zero, JDIMENSION samplesperrow, JDIMENSION numrows, JDIMENSION maxaccess)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10022D76
*/

static jvirt_barray_ptr request_virt_barray(j_common_ptr cinfo, int pool_id, boolean pre_zero, JDIMENSION blocksperrow, JDIMENSION numrows, JDIMENSION maxaccess)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10022E15
*/

static void realize_virt_arrays(j_common_ptr cinfo)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100230E4
*/

static JSAMPARRAY access_virt_sarray(j_common_ptr cinfo, jvirt_sarray_ptr ptr, JDIMENSION start_row, JDIMENSION num_rows, boolean writable)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x100232EE
*/

static void do_sarray_io(j_common_ptr cinfo, jvirt_sarray_ptr ptr, boolean writing)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1002343B
*/

static JBLOCKARRAY access_virt_barray(j_common_ptr cinfo, jvirt_barray_ptr ptr, JDIMENSION start_row, JDIMENSION num_rows, boolean writable)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10023648
*/

static void do_barray_io(j_common_ptr cinfo, jvirt_barray_ptr ptr, boolean writing)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x10023798
*/

static void free_pool(j_common_ptr cinfo, int pool_id)
{
}


/*
* Module:                 BBLibc.dll
* Entry point:            0x1002394E
*/

static void self_destruct(j_common_ptr cinfo)
{
}
