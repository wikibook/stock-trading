import React, { Component } from 'react';
import Grid from '@material-ui/core/Grid';
import { withStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import CodeSearch from '../components/CodeSearch';
import CodePrice from '../components/CodePrice';
import CodeChart from '../components/CodeChart';

const styles = {
    root: {
        flexGrow: 1,
    },
    paper: {
        height: 140,
        width: 100,
    },
    control: {
        padding: 2,
    },
};


class CodeInfo extends Component {
    constructor(props){
        super(props);
        this.state = {
            selectedCode:"",
        }
    }
    componentDidMount(){

    }
    componentDidUpdate(prevProps, prevState){

    }
    handleSelectedCode = (selectedCode)=>{
        console.log("CodeInfo handleSelectedCode", selectedCode);
        this.setState({selectedCode});
    }
    render(){
        return(
            <div>
                <div>
                    <CodeSearch code={this.state.selectedCode} handleSelectedCode={this.handleSelectedCode} />
                </div>
                <div>
                    <Grid>
                        <Grid container justify="left">
                            <Grid key={"codePrice"} item>
                                <CodePrice code={this.state.selectedCode}/>
                            </Grid>
                            <Grid key={"codeChart"} item>
                                <CodeChart code={this.state.selectedCode}/>
                            </Grid>
                        </Grid>
                    </Grid>
                </div>
            </div>
        );
    }
}

export default withStyles(styles)(CodeInfo);