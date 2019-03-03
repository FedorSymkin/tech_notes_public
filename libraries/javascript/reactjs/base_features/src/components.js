/*
Базовый пример работы с react.
Этот пример рендерит страницу, которая содержит:
	* Заголовок
	* Два элемента текста, один - обычными буквами, другой - то же самое upper case
	* набор кнопок с возможностью покрасить оба текста в разные цвета

Демонстрируются понятия:
	* Псевдо-тегов html и js внутри псевдо-тегов
	* props
	* state
*/

import React from "react";


export class Title extends React.Component {
  	render() { 
  		return (
  			<h2>ReactJs base features</h2>
  		); 
  	}
}


export class TextData extends React.Component {
	// Окошко с текстом (окошко потому что в css стилизовано)

	render() { 
		/*
			* Возвращается псевдо-html (jsx - расширение синтаксиса js)
			* в div прокидывается class = "text" для css
			* синтаксис {...} внутри этого псевдо-html означает, что там находится произвольный код на js,
				который что-то возвращает. То, что он возвращает, подставляется вместо {...} 
			* о том, что такое this.props и откуда оно берётся - ниже. Пока просто принимаем на веру, что каким-то образом снаружи 
				в этот объект приехало поле this.props, внутри которого есть color
		*/
		return (
			<div className="text">
			 	<font color={this.props.color}>
					{this.props.upper ? 'UPPER VERSION:' + this.props.text.toUpperCase() : 'original version: ' + this.props.text}
				</font>
			</div>
		); 
	}
}


export class ColorOption extends React.Component {
	//Кнопка выбора одного цвета

	render() { 
		/*	
			Здесь мы создаём обычный html-ный button, в обработчик клика которого ставим функцию этого же объекта handleChange.
			Важно сделать .bind(this), потому что в противном случае в handleChange this будет ссылаться не на этот объект. 
			Это грабли самого javascript.
		*/
		return (
			<div>
				<button className="btn" onClick={this.handleChange.bind(this)}>
					{this.props.color}
				</button>
			</div>
		); 
	}

	handleChange() {
		/*
			Обработчик события нажатия на кнопку внутри этого компонента.

		 	О том, что такое this.props и откуда оно берётся - ниже. 
		 	Пока просто принимаем на веру, что каким-то образом снаружи 
			в этот объект приехало поле this.props, внутри которого есть поле onChooseColor - некоторая функция.

			Мы просто её вызываем, и передаём туда другое поле из props
		*/
		this.props.onChooseColor(this.props.color);
	}
}


export class Options extends React.Component {	
	//Окошко с набором кнопок выбора цвета

	render() { 
		/*
			Здесь иллюстририуется сразу несколько понятий:

			* Тега ColorOption нет в html. Мы его сами придумали - у нас есть компонент ColorOption,
				и этот псевдо-html, который отбарабывает react, может содержать в себе такие теги, 
				основанные на других компонентах внутри нашего кода, как если бы это была спецификация html.

			* Свойства color и onChooseColor здесь тоже не из html. Это понятие props (свойства) - чуть выше по коду в компонентах
				мы обращались к this.props.something. Вот эти props как раз прокидывается здесь как атрибуты тегов

			* onChooseColor - это обычное свойство, но в качестве значения передаётся функция, которая потом дёргается изнутри ColorOption
				Здесь, как видно, сама эта функция тоже пришла извне в виде props. Т.е. компонент Options по сути только проксирует событие,
				но сам никак не реагирует на него.
		*/
		return (
			<div className="options">
				<ColorOption color="black" onChooseColor={this.props.onChooseColor}/>
				<ColorOption color="red" onChooseColor={this.props.onChooseColor}/>
				<ColorOption color="green" onChooseColor={this.props.onChooseColor}/>
				<ColorOption color="blue" onChooseColor={this.props.onChooseColor}/>
			</div>
		); 
	}
}


export default class Root extends React.Component {
 	constructor() {
 		super();
 		/*
	 		* Здесь демонстрируется ещё одна концепция: state. 
	 		* При изменении state происходит re-render виртуального DOM (т.е. вызывается функция render), 
	 			однако в реальном DOM меняется только то, что действительно нужно менять.
	 		* Как видно, про state знает только общий компонент Root, а не Options или ColorOption. При рендере данные state "спускаются" из Root-а
	 			по компонентам "вниз". Это позволяет писать чистый код и переиспользовать отдельные компоненты в разных проектах.
 		*/
 		this.state = {
 			text: "some data", 
 			color: "black"
 		}
 	}

	render() {
		/*
			* Возвращаем псевдо-теги html из наших компонентов (см. выше подробнее)
			* Пробрасываем нужные значения через props (см. выше что это такое)
			* Демонстрируется возможность повторного использования компонента (TextData с upper=true)
			* обработчик события onChooseColor тоже пробрасывается через props. И здесь опять же важно bind,
				для того чтобы this был правильным внутри функции onChooseColor (иначе this будет в контексте вызывающего кода)
		*/
    	return (
      		<div>
      			<Title />
      			<TextData text={this.state.text} color={this.state.color}/>
      			<TextData text={this.state.text} color={this.state.color} upper="true" />
      			<Options onChooseColor={this.onChooseColor.bind(this)} />
      		</div>
    	);
  	}

	onChooseColor(c) {
		/* 
			* Вызов этой функции пришёл "из глубины" - из объекта ColorOption (потому что мы передали эту функцию как свойтво в Options и дальше в глубину)
			* Здесь мы делаем setState (как видно можно не все поля указывать) и тем самым вызываем re-render виртуального DOM
			* Т.е. события идут из глубины наверх, а изменение состояния наоборот - сверху в глубину. Это один из основных принципов react.
		*/
		this.setState({
 			color: c
 		})
	}
}
