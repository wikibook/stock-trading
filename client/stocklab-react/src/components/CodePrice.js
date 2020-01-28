import React, { Component, forwardRef } from 'react';
import MaterialTable from "material-table";
import AddBox from '@material-ui/icons/AddBox';
import ArrowUpward from '@material-ui/icons/ArrowUpward';
import Check from '@material-ui/icons/Check';
import ChevronLeft from '@material-ui/icons/ChevronLeft';
import ChevronRight from '@material-ui/icons/ChevronRight';
import Clear from '@material-ui/icons/Clear';
import DeleteOutline from '@material-ui/icons/DeleteOutline';
import Edit from '@material-ui/icons/Edit';
import FilterList from '@material-ui/icons/FilterList';
import FirstPage from '@material-ui/icons/FirstPage';
import LastPage from '@material-ui/icons/LastPage';
import Remove from '@material-ui/icons/Remove';
import SaveAlt from '@material-ui/icons/SaveAlt';
import Search from '@material-ui/icons/Search';
import ViewColumn from '@material-ui/icons/ViewColumn';

const tableIcons = {
    Add: forwardRef((props, ref) => <AddBox {...props} ref={ref} />),
    Check: forwardRef((props, ref) => <Check {...props} ref={ref} />),
    Clear: forwardRef((props, ref) => <Clear {...props} ref={ref} />),
    Delete: forwardRef((props, ref) => <DeleteOutline {...props} ref={ref} />),
    DetailPanel: forwardRef((props, ref) => <ChevronRight {...props} ref={ref} />),
    Edit: forwardRef((props, ref) => <Edit {...props} ref={ref} />),
    Export: forwardRef((props, ref) => <SaveAlt {...props} ref={ref} />),
    Filter: forwardRef((props, ref) => <FilterList {...props} ref={ref} />),
    FirstPage: forwardRef((props, ref) => <FirstPage {...props} ref={ref} />),
    LastPage: forwardRef((props, ref) => <LastPage {...props} ref={ref} />),
    NextPage: forwardRef((props, ref) => <ChevronRight {...props} ref={ref} />),
    PreviousPage: forwardRef((props, ref) => <ChevronLeft {...props} ref={ref} />),
    ResetSearch: forwardRef((props, ref) => <Clear {...props} ref={ref} />),
    Search: forwardRef((props, ref) => <Search {...props} ref={ref} />),
    SortArrow: forwardRef((props, ref) => <ArrowUpward {...props} ref={ref} />),
    ThirdStateCheck: forwardRef((props, ref) => <Remove {...props} ref={ref} />),
    ViewColumn: forwardRef((props, ref) => <ViewColumn {...props} ref={ref} />)
  };

class CodePrice extends Component {
    constructor(props){
        super(props)
        this.state = {
            columns : [],//"date", "open", "high", "low", "close"],
            data:[],
        }
    }
    componentDidMount(){

    }
    componentDidUpdate(prevProps, prevState, snapshot){
        if(prevProps.code !== this.props.code){
            console.log("CodePrice componentDidupdate", this.props.code);
            let api_url = "http://127.0.0.1:5000/codes/"+this.props.code+"/price";
            fetch(api_url)
                .then(res => res.json())
                .then(data =>{
                    console.log("price didupdate fetch", data);
                    this.setState({columns : [{title:"날짜", field:"date"}, 
                                            {title:"시가", field:"open"}, 
                                            {title:"고가", field:"high"},
                                            {title:"저가", field:"low"},
                                            {title:"종가", field:"close"}]})
                    this.setState({data:data["price_list"]});
                }); 
        }
    }
    render(){
        return (
            <div>
                { this.state.data.length >0?
                    (<MaterialTable
                        icons={tableIcons}
                        title={"종목 가격정보"}
                        data={this.state.data}
                        columns={this.state.columns}
                    />):(null)
                }
            </div>
        );
    }
}

export default CodePrice;



