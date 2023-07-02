import React from "react";
import { BrowserRouter, Route, Link, Switch } from "react-router-dom";

import {Home, Messages, Options} from "./parts";


/*
Простейшая демонстрация принципов работы react-router-dom

На странице:
	* Менюшка с 3 ссылками
	* Заголовок
	* Какой-то контент, который зависит от выбранного пункта меню или от пути в браузере (почему фронтенд зависит от пути в браузере - об этом ниже)
	* Footer
*/


export default class Root extends React.Component {
	render() {
		//Про BrowserRouter подробнее в README. 
		//Здесь демонстрируется, что BrowserRouter не обязан быть корневым компонентов - Footer снаружи, это статика.
		return (
			<div>
				<BrowserRouter>
					<div>
						<Menu />
						<Main />	
					</div>
				</BrowserRouter>

				<Footer />
			</div>
		);
	}
}

export class Menu extends React.Component {
	render() {
		//Что такое Link - подробнее в README
		return (
			<div className="menu">
				<br/>MENU<br/><br/>
          		<Link to="/">Start page</Link><br/>
          		<Link to="/messages">View messages</Link><br/>
          		<Link to="/options">Set options</Link><br/>
			</div>
		);
	}
}


export class Main extends React.Component {
	render() {
		//Это для CSS отдельная сущность. Тут демонстрируется что статику (Title) можно
		//в принципе засовывать внутрь роутера
		return (
			<div className="main">
				<Title />
				<Workspace />
			</div>
		);
	}
}


class Title extends React.Component {
	render() {
		return (
			<div className="title">
	        	ReactJs routes example
			</div>
		);
	}
}


export class Workspace extends React.Component {
	render() {
		/*
			Здесь основное место. В этом примере в один момент времени активен только один Route,
			и это зависит от либо от кликнутого пункта меню, либо от пути в адресной строке, 
			с которым изначально пришёл пользователь.

			Несколько особенностей:
				* Это может изначально показаться странным, но путь в адресной строке браузера (например http://host/options)
					влияет не на то, что отдаст сервер, а на то, как поведёт себя фронт. Т.е. сервер как раз должен отдавать одну и 
					ту же страницу и тот же js для любого пути, которые участвует в роутинге (это конфигурится на сервере)
				* А фронт читает путь (типа window.location) и сразу выводит правильный компонент. Таким образом вся система для пользователя себя ведёт 
					как будто это обычный веб-сайт, а на самом деле это Single Page Application
				* свосйство exact здесь указано, потому что по умолчанию матчинг идёт по вхождению подстроки, иными словами без exact 
					запросы http://host/ и http://host/options будут оба матчиться в <Route exact path="/" component={Home}/>, потому что path является подстрокой 
					в обоих случаях. И тогда появится 2 компонента сразу. А если exact, то такого не будет
				* Здесь не показано, но в общем случае path не обязан быть точным, можно создавать Route с path="/some_resource/<some_id>", и для всех таких путей
					выводить один компонент, в котором ещё и перехватывать этот some_id

		*/
		return (
			<div className="workspace">
				<Switch>
			        <Route exact path="/" component={Home}/>
			        <Route exact path="/messages" component={Messages}/>
			        <Route exact path="/options" component={Options}/>
		        </Switch>
			</div>
		);
	}
}


export class Footer extends React.Component {
	render() {
		return (
			<div className="footer">
				footer: copyright and blah-blah-blah
			</div>
		);
	}
}
