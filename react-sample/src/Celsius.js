import React, { Component } from 'react';

class Celsius extends Component{
    constructor(props){
        super(props);
        this.state = {
            cValue: "", 
        }
        this.handleChange = this.handleChange.bind(this);
    }
    handleChange(event){
        console.log("Celsius", event.target.value);
        this.setState({cValue:event.target.value});
        this.props.handleCelsius(event.target.value);
    }
    render(){
        return(
            <div>
                섭씨:<input value={this.state.cValue} onChange={this.handleChange}></input>
            </div>
        );
    }
}

export default Celsius;