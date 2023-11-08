/* Call our flex scanner */
#include "Python.h"
#include <string.h>

#define STAR_SCANNER
#include "star_scanner.h"

#if PY_MAJOR_VERSION >= 3
  #define MOD_ERROR_VAL NULL
  #define MOD_SUCCESS_VAL(val) val
  #define MOD_INIT(name) PyMODINIT_FUNC PyInit_##name(void)
  #define MOD_DEF(ob, name, doc, methods) \
          static struct PyModuleDef moduledef = { \
            PyModuleDef_HEAD_INIT, name, doc, -1, methods, }; \
          ob = PyModule_Create(&moduledef);
#else
  #define MOD_ERROR_VAL
  #define MOD_SUCCESS_VAL(val)
  #define MOD_INIT(name) void init##name(void)
  #define MOD_DEF(ob, name, doc, methods) \
          ob = Py_InitModule3(name, methods, doc);
#endif

static PyObject * get_input(PyObject * self, PyObject * args);
static PyObject * flex_scan(PyObject * self,PyObject * args);
static PyObject * get_token(PyObject * self,PyObject * args);
static PyObject * drop_mem(PyObject * self,PyObject * args);
static PyObject * get_last_ten(PyObject * self,PyObject * args);

static PyMethodDef StarScanMethods[] = {
    {"prepare",get_input, METH_VARARGS,"Prepare scanner input"},
    {"scan", flex_scan, METH_VARARGS, "Get next token"},
    {"token",get_token, METH_VARARGS, "Return i'th token"},
    {"last_ten",get_last_ten, METH_VARARGS, "Return last 10 tokens"},
    {"cleanup", drop_mem, METH_VARARGS, "Free used memory"},
    {NULL,NULL,0,NULL}
    };

//Module initialisation for Python 2 and 3
MOD_INIT(StarScan)
{
  PyObject *m;
  MOD_DEF(m,"StarScan","A tokeniser for Star files",
          StarScanMethods)
    if(m==NULL)
      return MOD_ERROR_VAL;
    token_list =  NULL;
    value_list =  NULL;
    line_no_list = NULL;
    current_len = 0;
    alloc_mem = 0;
#if PY_MAJOR_VERSION >= 3
    return m;
#endif
}

/* We need to read from the text string that the Python
scanner uses, so we get a handle on the string and use
that to feed flex. We allow a Unicode string that is
UTF8 encoded. */

static PyObject * 
get_input(PyObject * self, PyObject * args) 
{
PyObject * str_arg;  /* A python string object in theory */
int i;
if(!(PyArg_ParseTuple(args,"U",&str_arg))) return NULL;
#if PY_MAJOR_VERSION >= 3
 input_string = PyUnicode_AsUTF8(str_arg);
#else
 input_string = PyString_AsString(str_arg);
#endif
string_pos = 0;
in_string_len = strlen(input_string);
star_clear();
for(i=0;i<current_len;i++){
  /* printf("New input, freeing value %d\n",i); */
    Py_XDECREF(value_list[i]);
    }
if(token_list!=NULL) {
/* printf("Freeing token_list\n"); */
free(token_list);}
if(value_list!=NULL) {
/* printf("Freeing value_list\n"); */
free(value_list);}
if(line_no_list!=NULL) {
free(line_no_list);}
alloc_mem = 0;
/* Now get our first block of storage */
token_list = (int *) malloc(MEM_ALLOC_SIZE*sizeof(int *));
value_list = (PyObject **) malloc(MEM_ALLOC_SIZE*sizeof(PyObject **));
line_no_list = (int *) malloc(MEM_ALLOC_SIZE*sizeof(int *));
alloc_mem += MEM_ALLOC_SIZE;
current_len = 0;
/* printf("New memory, val=%x,tok=%x\n",value_list,token_list);*/
return(Py_BuildValue(""));
}

/* Call our flex scanner and store the resulting token
in our internal list */

static PyObject *
flex_scan(PyObject * self, PyObject * args)
{
char * token_str;    /* String token */
char * save_str;     /* pointer to memory location */
size_t tok_len;      /* token length (no zero byte) */
int tok_id;          /* token id */
static char end_str[] = "END";
tok_id = star_scanner();
/* printf("Got token id %d i.e. %s\n",tok_id,tokens[tok_id]);*/
tok_len = yyleng;
if(tok_id == DEND) {
    /* printf("End seen\n");*/
    }
/* Get memory for storing token and value */
if(current_len+1>alloc_mem) {
    token_list = (int *) realloc(token_list,(alloc_mem+MEM_ALLOC_SIZE)*sizeof(int *));
    line_no_list = (int *) realloc(line_no_list,(alloc_mem+MEM_ALLOC_SIZE)*sizeof(int *));
    value_list = (PyObject **) realloc(value_list,(alloc_mem+MEM_ALLOC_SIZE)*sizeof(PyObject **));
    alloc_mem += MEM_ALLOC_SIZE;
    /* printf("Expanded memory, val=%x,tok=%x\n",value_list,token_list);*/
    }
/* store latest values */
save_str = (char *) malloc((yyleng+1)*sizeof(char *));
/* printf("Got memory for string %s length %d at %x\n",yytext,yyleng+1,save_str);*/
strncpy(save_str,yytext,yyleng+1);
value_list[current_len] = PyUnicode_FromString(save_str); /* new reference */
token_list[current_len] = tok_id;
line_no_list[current_len] = yylineno;
current_len++;
/* return(Py_BuildValue("(iiss)",0,0,token_str,yytext));*/
return(Py_BuildValue(""));
}

static PyObject *
get_token(PyObject * self, PyObject * args)
{
int list_pos; 
if(!(PyArg_ParseTuple(args,"i",&list_pos))) return NULL;
/* printf("Getting token %d\n",list_pos);*/
if(list_pos==current_len) flex_scan(self,args); 
if(list_pos<current_len)
    return(Py_BuildValue("(iisO)",line_no_list[list_pos],0,tokens[token_list[list_pos]],value_list[list_pos]));
else {
    PyErr_SetString(PyExc_IndexError,"No tokens left");
    return NULL;
    }
}

void
clear_mem(void)
{
int i;
for(i=0;i<current_len;i++){
  printf("Clearing token %d\n",i);
    Py_XDECREF(value_list[i]);
    }
free(token_list);
free(value_list);
free(line_no_list);
current_len = 0;
alloc_mem = 0;
}

static PyObject *
drop_mem(PyObject * self, PyObject * args)
{
clear_mem();
return NULL;
}

/* For error reporting we need to supply the last 10 tokens */

static PyObject *
get_last_ten(PyObject * self, PyObject * args)
{
int start_pt;
int ret_list_pos,pos_ptr;
PyObject * newlist;
PyObject * newtuple;     /* store each tuple */
if(current_len<=10) start_pt = 0;
else start_pt = current_len - 10;
newlist = PyList_New(current_len - start_pt);
for(ret_list_pos=0;start_pt+ret_list_pos<current_len;ret_list_pos++){
   pos_ptr = start_pt+ret_list_pos;
   /* printf("Build token %d\n",pos_ptr);*/
   newtuple = Py_BuildValue("iisO",line_no_list[pos_ptr],0,tokens[token_list[pos_ptr]],
                value_list[pos_ptr]);
   /* printf("Set list pos %d\n",ret_list_pos);*/
   PyList_SET_ITEM(newlist,ret_list_pos,newtuple);
}
return newlist;
}
