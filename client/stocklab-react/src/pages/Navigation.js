import React from 'react'; 
import { withStyles } from '@material-ui/core/styles';
import BottomNavigation from '@material-ui/core/BottomNavigation';
import BottomNavigationAction from '@material-ui/core/BottomNavigationAction';
import ListIcon from '@material-ui/icons/List';
import ShoppingCartIcon from '@material-ui/icons/ShoppingCart';
import CodeInfo from './CodeInfo';
import OrderInfo from './OrderInfo';

const styles = {
    bottom:{
        "width": "100%",
        "position": "fixed",
        "bottom": "0",
    }
};

class Navigation extends React.Component {
    constructor(props){
        super(props);
        this.state={
            value:0
        }
    }

    handleChange = (event, value) => {
        this.setState({ value });
    };

    render() {
        const { classes } = this.props;
        const { value } = this.state;

        return (
            <div className={classes.root}>
                <div>
                    {this.state.value === 0?
                        (<CodeInfo/>) : (<OrderInfo/>)
                    }
                </div>
                <BottomNavigation value={value} onChange={this.handleChange} 
                    showLabels className={classes.bottom}>
                    <BottomNavigationAction label="종목정보" value={0} icon={<ListIcon />} />
                    <BottomNavigationAction label="매매이력" value={1} icon={<ShoppingCartIcon/>} />
                </BottomNavigation>
            </div>
        );
    }
}

export default withStyles(styles)(Navigation);
