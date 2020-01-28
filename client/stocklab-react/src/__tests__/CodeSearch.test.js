import React from 'react';
import ReactDOM from 'react-dom';
import CodeSearch from '../components/CodeSearch';
import {render, fireEvent, cleanup} from 'react-testing-library';

beforeEach(() => {

});

afterEach(() => {

});

test('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<CodeSearch />, div);
  ReactDOM.unmountComponentAtNode(div);
});

