import React, { Component } from 'react';
import OrderList from '../components/OrderList';

class OrderInfo extends Component{
    constructor(props){
        super(props);
        this.state = {

        }
    }
    render(){
        return(
            <div>
                <OrderList />
            </div>
        );
    }
}

export default OrderInfo;