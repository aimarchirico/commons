import {folderRule} from '@aimarchirico/commons-ts/folders';
import baseConfig from './eslint';

export default [...baseConfig, folderRule()];
