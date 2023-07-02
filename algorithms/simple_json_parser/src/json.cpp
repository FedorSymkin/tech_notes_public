#include "json.h"
#include "helpers.h"

using namespace std;

namespace NJson {


enum class EFSMResult {GO_FURTHER, STAY_HERE}; // it may be bool, but enum makes code more readable
std::unique_ptr<IElement> ExtractSomething(TEscapedStringReader& reader);


TStringElement& IElement::AsString() {return dynamic_cast<TStringElement&>(*this);}
TArrayElement& IElement::AsArray() {return dynamic_cast<TArrayElement&>(*this);}
TObjectElement& IElement::AsObject() {return dynamic_cast<TObjectElement&>(*this);}


string TStringElement::Print() const
{
    stringstream res;
    res << "\"";
    for (const char c: Data) {
        char escaped = FactToEscaped(c);
        if (escaped)
            res << "\\" << escaped;
        else
            res << c;
    }
    res << "\"";
    return res.str();
}


string TArrayElement::Print() const
{
    stringstream res;

    res << "[";
    for (size_t i = 0; i < Data.size(); ++i) {
        if (i)
            res << ",";

        res << Data[i]->Print();
    }
    res << "]";

    return res.str();
}


string TObjectElement::Print() const
{
    stringstream res;

    res << "{";
    bool first = true;
    for (const auto& val: Data) {
        if (!first)
            res << ",";
        else
            first = false;

        res << "\"" << val.first << "\": " << val.second->Print();
    }
    res << "}";

    return res.str();
}


template <typename T>
class TBaseExtractor
{
protected:
    TEscapedStringReader& Reader;

protected:
    virtual EFSMResult Process(T& output) = 0;
    virtual bool Extracted() const = 0;

public:
    TBaseExtractor(TEscapedStringReader& reader) : Reader(reader) {}
    virtual ~TBaseExtractor() = default;

    unique_ptr<T> Extract()
    {
        auto output = std::make_unique<T>();
        T& outputRef = *output;

        while (!Reader.AtEnd() && !Extracted()) {
            if (Process(outputRef) == EFSMResult::GO_FURTHER)
                Reader.Next();
        }

        if (!Extracted()) {
            throw std::runtime_error("invalid json: data was not extracted");
        }

        return output;
    }
};


class TObjectExtractor : public TBaseExtractor<TObjectElement>
{
    enum class EState {
        WAITING_OPEN_BRACE,
        WAITING_NAME,
        PARSING_NAME,
        WAITING_COLON,
        WAITING_VALUE,
        PARSING_VALUE,
        WAITING_NEXT,
        FINISHED
    };

private:
    EState State = EState::WAITING_OPEN_BRACE;
    string CurrentName;

private:
    EFSMResult Process(TObjectElement& output) override
    {
        const TSymbol& symbol = Reader.Get();

        switch (State) {
            case EState::WAITING_OPEN_BRACE:
                if (symbol.IsSpace()) {
                    return EFSMResult::GO_FURTHER;
                }
                else if (symbol.Data != '{') {
                    throw std::runtime_error("invalid json, expected start of object");
                }
                else {
                    State = EState::WAITING_NAME;
                    return EFSMResult::GO_FURTHER;
                }

            case EState::WAITING_NAME:
                if (symbol.IsSpace()) {
                    return EFSMResult::GO_FURTHER;
                }
                else if (symbol.Data == '}') {
                    State = EState::FINISHED;
                    return EFSMResult::GO_FURTHER;
                }
                else if (!symbol.IsSystemQuote()) {
                    throw std::runtime_error("invalid json: expected start of name");
                }
                else {
                    CurrentName.clear();
                    State = EState::PARSING_NAME;
                    return EFSMResult::GO_FURTHER;
                }

            case EState::PARSING_NAME:
                if (symbol.IsSystemQuote()) {
                    State = EState::WAITING_COLON;
                    return EFSMResult::GO_FURTHER;
                }
                else {
                    CurrentName += symbol.Data;
                    return EFSMResult::GO_FURTHER;
                }

            case EState::WAITING_COLON:
                if (symbol.IsSpace()) {
                    return EFSMResult::GO_FURTHER;
                }
                else if (symbol.Data != ':') {
                    throw std::runtime_error("invalid json: expected colon");
                }
                else {
                    State = EState::WAITING_VALUE;
                    return EFSMResult::GO_FURTHER;
                }

            case EState::WAITING_VALUE:
                if (symbol.IsSpace()) {
                    return EFSMResult::GO_FURTHER;
                }
                else {
                    State = EState::PARSING_VALUE;
                    return EFSMResult::STAY_HERE;
                }

            case EState::PARSING_VALUE:
                if (output.Data.find(CurrentName) != output.Data.end())
                    throw std::runtime_error("invalid json, duplicate name: " + CurrentName);

                output.Data[CurrentName] = ExtractSomething(Reader);
                CurrentName.clear();
                State = EState::WAITING_NEXT;
                return EFSMResult::STAY_HERE;

            case EState::WAITING_NEXT:
                if (symbol.IsSpace()) {
                    return EFSMResult::GO_FURTHER;
                }
                else if (symbol.Data == ',') {
                    State = EState::WAITING_NAME;
                    return EFSMResult::GO_FURTHER;
                }
                else if (symbol.Data == '}') {
                    State = EState::FINISHED;
                    return EFSMResult::GO_FURTHER;
                }
                else {
                    throw std::runtime_error("invalid json: expected comma or end of object");
                }

            case EState::FINISHED:
                return EFSMResult::STAY_HERE;

            default:
                throw std::runtime_error("unknown state");
        }
    }

    bool Extracted() const override
    {
        return State == EState::FINISHED;
    }

public:
    TObjectExtractor(TEscapedStringReader& reader): TBaseExtractor(reader) {}
};


class TArrayExtractor : public TBaseExtractor<TArrayElement>
{
    enum class EState {
        WAITING_OPEN_BRACE,
        WAITING_VALUE,
        PARSING_VALUE,
        WAITING_NEXT,
        FINISHED
    };

private:
    EState State = EState::WAITING_OPEN_BRACE;

private:
    EFSMResult Process(TArrayElement& output) override
    {
        const TSymbol& symbol = Reader.Get();

        switch (State) {
            case EState::WAITING_OPEN_BRACE:
                if (symbol.IsSpace()) {
                    return EFSMResult::GO_FURTHER;
                }
                else if (symbol.Data != '[') {
                    throw std::runtime_error("invalid json: expected start of array");
                }
                else {
                    State = EState::WAITING_VALUE;
                    return EFSMResult::GO_FURTHER;
                }

            case EState::WAITING_VALUE:
                if (symbol.IsSpace()) {
                    return EFSMResult::GO_FURTHER;
                }
                else if (symbol.Data == ']') {
                    State = EState::FINISHED;
                    return EFSMResult::GO_FURTHER;
                }
                else {
                    State = EState::PARSING_VALUE;
                    return EFSMResult::STAY_HERE;
                }

            case EState::PARSING_VALUE:
                output.Data.push_back(ExtractSomething(Reader));
                State = EState::WAITING_NEXT;
                return EFSMResult::STAY_HERE;

            case EState::WAITING_NEXT:
                if (symbol.IsSpace()) {
                    return EFSMResult::GO_FURTHER;
                }
                else if (symbol.Data == ',') {
                    State = EState::WAITING_VALUE;
                    return EFSMResult::GO_FURTHER;
                }
                else if (symbol.Data == ']') {
                    State = EState::FINISHED;
                    return EFSMResult::GO_FURTHER;
                }
                else {
                    throw std::runtime_error("invalid json: expected comma or array end");
                }

            case EState::FINISHED:
                return EFSMResult::STAY_HERE;

            default:
                throw std::runtime_error("unknown state");
        }
    }

    bool Extracted() const override
    {
        return State == EState::FINISHED;
    }

public:
    TArrayExtractor(TEscapedStringReader& reader) : TBaseExtractor(reader) {}
};


class TStringExtractor : public TBaseExtractor<TStringElement>
{
    enum class EState {
        WAITING_OPEN_QUOTE,
        PARSING_VALUE,
        FINISHED
    };

private:
    EState State = EState::WAITING_OPEN_QUOTE;

private:
    EFSMResult Process(TStringElement& output) override
    {
        const TSymbol& symbol = Reader.Get();

        switch (State) {
            case EState::WAITING_OPEN_QUOTE:
                if (symbol.IsSpace()) {
                    return EFSMResult::GO_FURTHER;
                }
                else if (!symbol.IsSystemQuote()) {
                    throw std::runtime_error("invalid json: expected open quote for string");
                }
                else {
                    State = EState::PARSING_VALUE;
                    return EFSMResult::GO_FURTHER;
                }

            case EState::PARSING_VALUE:
                if (symbol.IsSystemQuote()) {
                    State = EState::FINISHED;
                    return EFSMResult::GO_FURTHER;
                }
                else {
                    output.Data += symbol.Data;
                    return EFSMResult::GO_FURTHER;
                }

            case EState::FINISHED:
                return EFSMResult::STAY_HERE;

            default:
                throw std::runtime_error("unknown state");
        }
    }

    bool Extracted() const override
    {
        return State == EState::FINISHED;
    }

public:
    TStringExtractor(TEscapedStringReader& reader) : TBaseExtractor(reader) {}
};


std::unique_ptr<IElement> ExtractSomething(TEscapedStringReader& reader)
{
    const TSymbol& symbol = reader.Get();

    if (symbol.Data == '{') {
        return TObjectExtractor(reader).Extract();
    }
    else if (symbol.Data == '[') {
        return TArrayExtractor(reader).Extract();
    }
    else if (symbol.IsSystemQuote()) {
        return TStringExtractor(reader).Extract();
    }
    else {
        throw std::runtime_error("unexpected data type");
    }
}


unique_ptr<TObjectElement> Parse(const string& src)
{
    TEscapedStringReader reader(src);
    reader.Next();

    try {
        auto res = TObjectExtractor(reader).Extract();

        reader.MoveToNoSpaceSymbol();
        if (!reader.AtEnd())
            throw std::runtime_error("invalid json: trash after json object");

        return res;
    }
    catch (const std::exception& e) {
        throw std::runtime_error("error at position " + to_string(reader.GetPos()) + ": " + string(e.what()));
    }
}


} //namespace
