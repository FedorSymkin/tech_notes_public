#include "helpers.h"

namespace NJson {

char EscapedToFact(char escaped)
{
    switch (escaped) {
        case 'n': return '\n';
        case 't': return '\t';
        case '\\': return '\\';
        case '"': return '"';
        default: return 0;
    }
}

char FactToEscaped(char fact)
{
    switch (fact) {
        case '\n': return 'n';
        case '\t': return 't';
        case '\\': return '\\';
        case '"': return '"';
        default: return 0;
    }
}

} //namespace
