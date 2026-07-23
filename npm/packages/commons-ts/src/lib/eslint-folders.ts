import {folderRule} from './folders';
import baseConfig from './eslint-base';

export default [...baseConfig, folderRule()];
