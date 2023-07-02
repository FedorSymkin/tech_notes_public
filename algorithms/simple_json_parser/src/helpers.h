#pragma once

#include <string>
#include <stdexcept>

namespace NJson {

char EscapedToFact(char escaped);
char FactToEscaped(char fact);

struct TSymbol
{
    char Data = 0;
    bool Escaped = false;

    void Set(char data, bool escaped)
    {
        Data = data;
        Escaped = escaped;
    }

    bool IsSpace() const
    {
        return Data == ' ' || Data == '\t' || Data == '\n';
    }

    bool IsSystemQuote() const
    {
        return Data == '\"' && !Escaped;
    }
};

class TEscapedStringReader
{
private:
    const std::string& Src;
    std::string::const_iterator Pos;
    bool WasSlash = false;
    bool Started = false;
    TSymbol CurrentSymbol;

private:
    void MoveForward()
    {
        if (!Started) {
            Started = true;
        }
        else {
            ++Pos;
        }
    }

public:
    TEscapedStringReader(const std::string& src)
        : Src(src)
        , Pos(Src.cbegin())
    {}

    void Next()
    {
        if (AtEnd()) {
            CurrentSymbol.Set(0, false);
            return;
        }

        MoveForward();
        char c = *Pos;

        if (WasSlash) {
            char fact = EscapedToFact(c);
            if (!fact)
                throw std::runtime_error("unknown escaped sequence: \\" + std::string(1, c));

            WasSlash = false;
            CurrentSymbol.Set(fact, true);
        }
        else if (c == '\\') {
            WasSlash = true;
            Next();
        }
        else {
            CurrentSymbol.Set(c, false);
        }
    }

    void MoveToNoSpaceSymbol()
    {
        while (!AtEnd() && CurrentSymbol.IsSpace())
            Next();
    }

    const TSymbol& Get() const
    {
        return CurrentSymbol;
    }

    size_t GetPos() const
    {
        return std::distance(Src.begin(), Pos);
    }

    bool AtEnd() const
    {
        return Pos == Src.end();
    }
};


} //namespace
