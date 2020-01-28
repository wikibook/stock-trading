import React, { Component } from 'react';
//import MUIDataTable from "mui-datatables";
//import Chart from 'react-google-charts';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, } from 'recharts';
 

class CodeChart extends Component {
    constructor(props){
        super(props)
        this.state = {
            data:[],
        }
    }
    componentDidMount(){

    }

    componentDidUpdate(prevProps, prevState, snapshot){
       if(prevProps.code !== this.props.code){
            console.log("CodeChart componentDidupdate", this.props.code);
            let api_url = "http://127.0.0.1:5000/codes/"+this.props.code+"/price";
            let resultDataList = []
            fetch(api_url)
                .then(res => res.json())
                .then(data =>{
                    this.setState({data: data["price_list"]});
                }); 
        }
    }

    render(){
        console.log("CodeChart render", this.state.data);
        return (
            <div>
            {this.state.data.length >0 ?
                (
                    <LineChart width={500} height={300} data={this.state.data} 
                        margin={{ top: 5, right: 30, left: 20, bottom: 5, }} >
                    <XAxis dataKey="date" />
                    <YAxis/>
                    <Legend />
                    <Line type="monotone" dataKey="close" stroke="#8884d8" activeDot={{ r: 8 }} />
                    </LineChart>
                ):(null)
            }
            </div>
        );
    }
}

export default CodeChart;