# cython

* Прослойка между python и C/C++, позволяющая запускать код на C/C++ из питона.
* Формально это язык программирования

## Как запускать
* `make install_deps`
* `make`
* `python check.py`

## Из чего состоит
* `exapmles.cpp` и `examples.h` - исходный код на C++
* `pyexamples.pyx` - код на cython, обвязка между миром cpp и миром py
* `setup.py` - инструкции как собирать cython модуль
* `check.py` - пример вызова cython-функции из питона.

## Как работает
* Сначала собирается модуль cython в виде so-библиотеки (генерится `pyexamples.so`). 
* Это делается с помощью команды `python setup.py build_ext --inplace`
* Внутри `setup.py` указано имя модуля, исходники (одновременно обвязка pyx и cpp код), include_dirs. Собственно сборка выполняется на вызове distutils.core.setup
* Далее в обычном питоне (`check.py`) просто испортируем этот so-модуль как обычный питонячий модуль:
`import pyexamples`
* И просто вызываем из него фунцию
* Надо обратить внимание, что передаётся не питонячая строка `world`, а байты `b"world"`, потому что функция hello ожидает на вход сырую C-шную строку
* Не забываем указать extern "C" в cpp файле, иначе работать не будет.

## Немного подробностей
* Сборка so-библиотеки в setup.py идёт так (видно, что там ещё промежуточный файл pyexamples.c генерится):
```
x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -fno-strict-aliasing -Wdate-time -D_FORTIFY_SOURCE=2 -g -fstack-protector-strong -Wformat -Werror=format-security -fPIC -I. -I/usr/include/python2.7 -c pyexamples.c -o build/temp.linux-x86_64-2.7/pyexamples.o

x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -fno-strict-aliasing -Wdate-time -D_FORTIFY_SOURCE=2 -g -fstack-protector-strong -Wformat -Werror=format-security -fPIC -I. -I/usr/include/python2.7 -c examples.cpp -o build/temp.linux-x86_64-2.7/examples.o
```

* Внутренности so-библиотеки
```
$ nm -C pyexamples.so
0000000000204368 B __bss_start
0000000000204380 b completed.7585
                 U __cxa_atexit@@GLIBC_2.2.5
                 w __cxa_finalize@@GLIBC_2.2.5
0000000000002270 t deregister_tm_clones
0000000000002300 t __do_global_dtors_aux
0000000000203d80 t __do_global_dtors_aux_fini_array_entry
00000000002041a0 d __dso_handle
0000000000204360 d DW.ref.__gxx_personality_v0
0000000000203d90 d _DYNAMIC
0000000000204368 D _edata
0000000000204478 B _end
0000000000002cf4 T _fini
0000000000002340 t frame_dummy
0000000000203d70 t __frame_dummy_init_array_entry
00000000000030d0 r __FRAME_END__
0000000000204000 d _GLOBAL_OFFSET_TABLE_
0000000000002240 t _GLOBAL__sub_I_examples.cpp
                 w __gmon_start__
0000000000002e78 r __GNU_EH_FRAME_HDR
                 U __gxx_personality_v0@@CXXABI_1.3
0000000000002b30 T hello
00000000000018b8 T _init
0000000000001c00 T initpyexamples
                 w _ITM_deregisterTMCloneTable
                 w _ITM_registerTMCloneTable
0000000000203d88 d __JCR_END__
0000000000203d88 d __JCR_LIST__
                 w _Jv_RegisterClasses
                 U memcpy@@GLIBC_2.14
                 U _PyByteArray_empty_string
                 U PyByteArray_Type
                 U PyCFunction_NewEx
                 U PyCode_New
                 U PyDict_GetItem
                 U PyDict_New
                 U PyDict_SetItem
                 U PyErr_Clear
                 U PyErr_Occurred
                 U PyErr_SetString
                 U PyErr_WarnEx
                 U PyExc_ImportError
                 U PyFrame_New
                 U Py_GetVersion
                 U PyImport_AddModule
                 U Py_InitModule4_64
                 U PyMem_Malloc
                 U PyMem_Realloc
                 U PyModule_GetDict
                 U _Py_NoneStruct
                 U PyObject_GetAttr
                 U _PyObject_GetDictPtr
                 U PyObject_Hash
                 U PyObject_Not
                 U PyObject_SetAttr
                 U PyObject_SetAttrString
                 U PyOS_snprintf
                 U PyString_AsStringAndSize
                 U PyString_FromFormat
                 U PyString_FromString
                 U PyString_FromStringAndSize
                 U PyString_InternFromString
                 U _PyThreadState_Current
                 U PyTraceBack_Here
                 U _Py_TrueStruct
                 U PyTuple_New
                 U PyTuple_Pack
                 U PyType_IsSubtype
                 U PyUnicodeUCS4_DecodeUTF8
                 U PyUnicodeUCS4_FromStringAndSize
00000000000023f0 t __Pyx_AddTraceback
0000000000204458 b __pyx_b
0000000000002370 t __pyx_bisect_code_objects
0000000000204438 b __pyx_clineno
0000000000204420 b __pyx_code_cache
0000000000204450 b __pyx_cython_runtime
0000000000204460 b __pyx_d
0000000000204440 b __pyx_empty_bytes
0000000000204448 b __pyx_empty_tuple
0000000000204430 b __pyx_filename
0000000000002dd0 r __pyx_k_cline_in_traceback
0000000000002e38 r __pyx_k_main
0000000000002e28 r __pyx_k_name
0000000000002e11 r __pyx_k_name_2
00000000002043e8 b __pyx_kp_s_pyexamples_pyx
0000000000002df8 r __pyx_k_pyexamples
0000000000002de8 r __pyx_k_pyexamples_pyx
0000000000002e08 r __pyx_k_py_hello
0000000000002e18 r __pyx_k_test
000000000020443c b __pyx_lineno
0000000000204468 b __pyx_m
0000000000204340 d __pyx_mdef_10pyexamples_1py_hello
00000000002043c0 b __pyx_methods
00000000002043a0 B __pyx_module_is_main_pyexamples
0000000000204418 b __pyx_n_s_cline_in_traceback
0000000000204410 b __pyx_n_s_main
0000000000204408 b __pyx_n_s_name
0000000000204400 b __pyx_n_s_name_2
00000000002043f0 b __pyx_n_s_pyexamples
00000000002043f8 b __pyx_n_s_py_hello
00000000002043e0 b __pyx_n_s_test
0000000000002a20 t __pyx_pw_10pyexamples_1py_hello
00000000002041c0 d __pyx_string_tab
                 U _Py_ZeroStruct
00000000000022b0 t register_tm_clones
                 U __stack_chk_fail@@GLIBC_2.4
                 U strlen@@GLIBC_2.2.5
0000000000204368 d __TMC_END__
                 U _Unwind_Resume@@GCC_3.0
                 U operator delete(void*)@@GLIBCXX_3.4
                 U std::ctype<char>::_M_widen_init() const@@GLIBCXX_3.4.11
0000000000002cf0 W std::ctype<char>::do_widen(char) const
                 U std::ostream::put(char)@@GLIBCXX_3.4
                 U std::ostream::flush()@@GLIBCXX_3.4
                 U std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >::_M_create(unsigned long&, unsigned long)@@GLIBCXX_3.4.21
                 U std::ios_base::Init::Init()@@GLIBCXX_3.4
                 U std::ios_base::Init::~Init()@@GLIBCXX_3.4
                 U std::basic_ostream<char, std::char_traits<char> >& std::__ostream_insert<char, std::char_traits<char> >(std::basic_ostream<char, std::char_traits<char> >&, char const*, long)@@GLIBCXX_3.4.9
                 U std::__throw_bad_cast()@@GLIBCXX_3.4
                 U std::__throw_logic_error(char const*)@@GLIBCXX_3.4
                 U std::cout@@GLIBCXX_3.4
0000000000204470 b std::__ioinit
```