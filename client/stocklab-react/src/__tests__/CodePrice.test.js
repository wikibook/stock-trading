import React from 'react';
import ReactDOM from 'react-dom';
import CodePrice from '../components/CodePrice';
import {render, fireEvent, cleanup} from 'react-testing-library';

beforeEach(() => {

});

afterEach(() => {

});

test('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<CodePrice />, div);
  ReactDOM.unmountComponentAtNode(div);
});


