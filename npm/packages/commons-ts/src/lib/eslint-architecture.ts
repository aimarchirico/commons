import {folderRule} from './folders';
import baseConfig from './eslint';

export default [...baseConfig, folderRule()];
