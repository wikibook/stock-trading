import React from 'react';
import ReactDOM from 'react-dom';
import CodeChart from '../components/CodeChart';
import {render, fireEvent, cleanup} from 'react-testing-library';

beforeEach(() => {

});

afterEach(() => {

});

test('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<CodeChart />, div);
  ReactDOM.unmountComponentAtNode(div);
});

