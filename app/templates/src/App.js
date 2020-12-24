
//import Search from './components/Search.js';

import logo from './assets/logo.png';
import './App.css';
import { ReactComponent as Loader } from './assets/loading.svg';
import { Fragment, useEffect, useState} from 'react';
import { RecoilRoot, atom, useRecoilState} from 'recoil';
import { Donut } from 'britecharts-react';


const ENDPOINT = '/predict';

const State = atom({
	key: 'State',
	default: {
		url: '',
		maxPages: 30,
		loading: false,
		input: null,
		error: false,
		data: {
			opinions:{}
		}
	}
});

const Search = (props) => {
	
	const [state, setState] = useRecoilState(State);

	const handleSubmit = (event) =>{
		event.preventDefault();
		const input = event.target[0];
		if (!state.loading){
			setState({ ...state, url: input.value, input: input});
			input.disabled = true;
			input.parentElement.parentElement.style.marginTop = 0;
		}
	};

	const handleInputChange = () => {
		if (!state.loading && state.input != null) {
			state.input.parentElement.parentElement.style.marginTop = '50%';
			setState({...state, url: '', error: false});
		}
	}

	useEffect(() => {
		if (!state.loading && state.input != null) state.input.disabled = false;
	}, [state.data, state.error]);


	return (
		<article className="search">
			<img src={logo} alt="AmazonSentiment" width={300} />
			<form className="search--query" onSubmit={handleSubmit}>
				<input type="text" name="url" placeholder="Amazon product's url" onChange={handleInputChange}/>
				<button className="fa fa-search" type="submit"></button>
			</form>
		</article>
	);
}

const Opinion = (props) => {
	const [state, setState] = useState({
		data: [
			{
				quantity: props.data.percentage[0],
				percentage: props.data.percentage[0],
				name: 'positive',
				id: 1
			},
			{
				quantity: props.data.percentage[1],
				percentage: props.data.percentage[1],
				name: 'neutral',
				id: 2
			},
			{
				quantity: props.data.percentage[2],
				percentage: props.data.percentage[2],
				name: 'negative',
				id: 3
			}
		],
		highlightedSlice: 1,
		selected: false
	});

	const width = 200;
	const percentageMax = props.data.percentage.indexOf(Math.max(...props.data.percentage)) + 1
	const style = [{ 'color': 'rgb(106, 237, 199)' }, { 'color': 'rgb(57, 194, 201)' }, { 'color': 'rgb(255, 206, 0)' }][percentageMax-1];

	const handleMouseOver = (data) => {
		if(!state.selected) setState({...state,	highlightedSlice: data.data.id, selected: true});
	}

	const handleMouseOut = () => {
		setState({ ...state, highlightedSlice: percentageMax, selected: false});
	}
	
	useEffect(() => {});

	return(
		<div className="opinion">
			<Donut
				data={state.data}
				height={width}
				width={width}
				externalRadius={width / 2.5}
				internalRadius={width / 5}
				isAnimated={false}
				highlightSliceById={ state.highlightedSlice}
				customMouseOver={handleMouseOver.bind(this)}
				customMouseOut={handleMouseOut.bind(this)}
			/>
			<h2 style={style}>{props.name}</h2>
			<h4>Impact : {props.data.weight} %</h4>
		</div>
	);
}

const Result = () => {

	const [state, setState] = useRecoilState(State);

	const fetchAPI = async () => {
		console.log("Fetching ...");
		setState({ ...state, loading: true });

		try{
			const response = await fetch(ENDPOINT, {
				headers: {
					'Accept': 'application/json',
					'Content-Type': 'application/json'
				},
				method: 'POST',
				body: JSON.stringify({ url: state.url, maxPages: state.maxPages })
			})

			const data = await response.json();

			const computed = Object.entries(data.opinions)
				.sort(([, a], [, b]) => b.weight - a.weight)
				.reduce((r, [k, v]) => ({ ...r, [k]: v }), {});


			setState({ ...state, loading: false, data: { ...data, opinions: computed } });
		}catch(err){
			console.log(err);
			setState({...state, loading: false, error: true});
		}
		
	}

	useEffect(() => {
		let mounted = true;
		
		if (mounted && state.url.length > 0 ) fetchAPI();
		
		return () => mounted = false;

	}, [state.url])

	return (
		<Fragment>
			{state.loading && state.url.length > 0 && !state.error &&
				<Fragment>
					<Loader />
					<span className="box info">
						<h1>We collecting and analyzing your product's comments</h1>
						<h2>Please wait few seconds ...</h2>
					</span>
				</Fragment>
			}
			{!state.loading && state.url.length > 0 && !state.error &&
				<Fragment>
					<article className="product">
						<div className="left">
							<img src={state.data.img} alt="Product picture" />
						</div>
						<div className="middle">
							<h3>{state.data.name}</h3>
							<h2>{state.data.price} | {state.data.note} ⭐ | {state.data.reviews} ✍️</h2>
							<p>{state.data.desc}</p>
						</div>
					</article>
					{Object.keys(state.data.opinions).length > 0 &&
					<article className="full-bleed">
						<div className="opinions">
							{Object.keys(state.data.opinions).map((opinion) => <Opinion name={opinion} data={state.data.opinions[opinion]} />)}
						</div>
					</article>
					}
					{Object.keys(state.data.opinions).length == 0 &&
						<div className="box warn">
							<h1>Aucun opinion detecté 😟</h1>
						</div>
					}
				</Fragment>
			}
			{state.error &&
				<div className="box warn">
					<h1>A non-Amazonian product 😟</h1>
				</div>
			}
		</Fragment>
	);
}


const App = () => {

	
	return (
		<RecoilRoot>
			<section className="wrapper">
				<Search />
				<Result />
			</section>
		</RecoilRoot>
	);
}

export default App;