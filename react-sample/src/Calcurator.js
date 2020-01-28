import React, { Component } from 'react';
import Celsius from './Celsius';
import Fahrenheit from './Fahrenheit';

class Calculator extends Component{
    constructor(props){
        super(props);
        this.state = {
            result:"",
            cValue:0.0,
        }
    }
    handleClick=(event)=>{
        console.log("Click");
        this.setState({result:this.state.cValue*(9/5)+32});
    }
    handleCelsius=(value)=>{
        console.log("Calculator handleCelsius", value);
        this.setState({cValue:parseFloat(value)});
    }

    render(){
        return(
            <div>
                <Celsius handleCelsius={this.handleCelsius} />
                <Fahrenheit result={this.state.result} />
                <button onClick={this.handleClick}>Change</button>
            </div>
        );
    }
}

export default Calculator;