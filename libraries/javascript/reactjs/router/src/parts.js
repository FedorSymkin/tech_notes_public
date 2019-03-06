import React from "react";


/*
Сюда выведены компоненты, которые динамически появляются и исчезают при выборе меню
*/


export class Home extends React.Component {
	render() {
		return (
			<div>
				Hello world! This is main page, where you can read summary info!
			</div>
		);
	}
}


class Message extends React.Component {
	render() {
		return (
			<div class="message">
				{this.props.text}
			</div>
		);
	}
}


export class Messages extends React.Component {
	render() {
		return (
			<div>
				<Message text="message1" />
				<Message text="message2" />
				<Message text="message3" />
			</div>
		);
	}
}


class Option extends React.Component {
	render() {
		return (
			<button class="option" onClick={this.onClick.bind(this)}>
				{this.props.name}
			</button>
		);
	}

	onClick() {
		alert("option: " + this.props.name);
	}
}


export class Options extends React.Component {
	render() {
		return (
			<div>
				<div><Option name="option1" /></div>
				<div><Option name="option2" /></div>
				<div><Option name="option3" /></div>
			</div>
		);
	}
}
