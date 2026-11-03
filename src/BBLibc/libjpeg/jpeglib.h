/*
 * Declarations of types of IJG libjpeg 6b used by signatures of its
 * procedures in BBLibc.dll.
 *
 * It isn't the original jpeglib.h: structures are declared without fields
 * and enumerations are 'int', BldRecompile doesn't need more for now.
 * Types are collected from jpeglib.h, jmorecfg.h, jconfig.vc, jpegint.h,
 * jdct.h, jchuff.h, jdhuff.h and jmemsys.h of libjpeg 6b.
 */

/* jconfig.vc: 'boolean' is 'unsigned char' in BBLibc.dll */
typedef unsigned char boolean;

/* jmorecfg.h */
typedef unsigned char JSAMPLE;
typedef short JCOEF;
typedef unsigned char JOCTET;
typedef unsigned char UINT8;
typedef unsigned short UINT16;
typedef short INT16;
typedef long INT32;
typedef unsigned int JDIMENSION;

/* jpeglib.h */
typedef JSAMPLE * JSAMPROW;
typedef JSAMPROW * JSAMPARRAY;
typedef JSAMPARRAY * JSAMPIMAGE;
typedef JCOEF JBLOCK[64];
typedef JBLOCK * JBLOCKROW;
typedef JBLOCKROW * JBLOCKARRAY;
typedef JBLOCKARRAY * JBLOCKIMAGE;
typedef JCOEF * JCOEFPTR;

struct JQUANT_TBL;
struct JHUFF_TBL;
struct jpeg_component_info;
struct jpeg_scan_info;
struct jpeg_common_struct;
struct jpeg_compress_struct;
struct jpeg_decompress_struct;
struct jpeg_error_mgr;
struct jvirt_sarray_control;
struct jvirt_barray_control;

typedef struct jpeg_common_struct * j_common_ptr;
typedef struct jpeg_compress_struct * j_compress_ptr;
typedef struct jpeg_decompress_struct * j_decompress_ptr;
typedef struct jvirt_sarray_control * jvirt_sarray_ptr;
typedef struct jvirt_barray_control * jvirt_barray_ptr;

/* enum J_COLOR_SPACE */
typedef int J_COLOR_SPACE;

/* boolean (*jpeg_marker_parser_method) (j_decompress_ptr cinfo) */
typedef void * jpeg_marker_parser_method;

/* jpegint.h: enum J_BUF_MODE */
typedef int J_BUF_MODE;

/* jdct.h */
typedef int DCTELEM;
typedef float FAST_FLOAT;

/* jchuff.h */
struct c_derived_tbl;

/* jdhuff.h */
struct d_derived_tbl;
struct bitread_working_state;
typedef INT32 bit_buf_type;

/* jmemsys.h */
struct backing_store_struct;
typedef struct backing_store_struct * backing_store_ptr;
