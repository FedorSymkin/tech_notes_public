#pragma once

#include <string>
#include <vector>
#include <unordered_map>
#include <sstream>
#include <memory>

namespace NJson {


enum class EElementType { STRING, ARRAY, OBJECT };


class TStringElement;
class TArrayElement;
class TObjectElement;


struct IElement
{
    virtual ~IElement() = default;

    virtual std::string Print() const = 0;
    virtual EElementType Type() const = 0;

    TStringElement& AsString();
    TArrayElement& AsArray();
    TObjectElement& AsObject();
};


struct TStringElement : public IElement
{
    std::string Data;

    EElementType Type() const override {return EElementType::STRING;}
    std::string Print() const override;
};


struct TArrayElement : public IElement
{
    std::vector<std::unique_ptr<IElement>> Data;

    EElementType Type() const override {return EElementType::ARRAY;}
    std::string Print() const override;
};


struct TObjectElement : public IElement
{
    std::unordered_map<std::string, std::unique_ptr<IElement>> Data;

    EElementType Type() const override {return EElementType::OBJECT;}
    std::string Print() const override;
};


std::unique_ptr<TObjectElement> Parse(const std::string& src);


} //namespace
