import {defineConfig} from 'sanity';
import {structureTool} from 'sanity/structure';
import {visionTool} from '@sanity/vision';
import {portfolioProject} from './schemaTypes/project';

const projectId = process.env.SANITY_STUDIO_PROJECT_ID || 'your-project-id';
const dataset = process.env.SANITY_STUDIO_DATASET || 'production';

export default defineConfig({
  name: 'sofiia-portfolio',
  title: 'SOFIIA / Portfolio Studio',
  projectId,
  dataset,
  plugins: [structureTool(), visionTool()],
  schema: {types: [portfolioProject]},
});
