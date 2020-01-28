import React, { Component } from 'react';

class Fahrenheit extends Component{
    constructor(props){
        super(props);
        this.state = {
        }
    }
    render(){
        return(
            <div>
                <label>화씨: {this.props.result}</label>
            </div>
        );
    }
}

export default Fahrenheit;