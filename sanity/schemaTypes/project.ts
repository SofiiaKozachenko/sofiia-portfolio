import {defineField, defineType} from 'sanity';

export const portfolioProject = defineType({
  name: 'portfolioProject',
  title: 'Portfolio project',
  type: 'document',
  fields: [
    defineField({name:'title',title:'Project name',type:'string',validation:Rule=>Rule.required()}),
    defineField({name:'slug',title:'Page URL',type:'slug',options:{source:'title'},validation:Rule=>Rule.required()}),
    defineField({name:'subtitle',title:'Short category / subtitle',type:'string'}),
    defineField({name:'category',title:'Filter category',type:'string',options:{list:[{title:'Brand identity',value:'branding'},{title:'UI / Digital',value:'digital'},{title:'Packaging',value:'packaging'}],layout:'radio'},validation:Rule=>Rule.required()}),
    defineField({name:'type',title:'Type label',type:'string',description:'Example: BRAND IDENTITY or UI / UX DESIGN'}),
    defineField({name:'year',title:'Year',type:'string'}),
    defineField({name:'orderRank',title:'Display order (1, 2, 3...)',type:'number',initialValue:99}),
    defineField({name:'palette',title:'Card color',type:'string',options:{list:['violet','peach','lime','brown','blue']},initialValue:'blue'}),
    defineField({name:'short',title:'Short description (English)',type:'text',rows:2}),
    defineField({name:'shortUa',title:'Short description (Ukrainian)',type:'text',rows:2}),
    defineField({name:'description',title:'Case story (English)',type:'text',rows:5}),
    defineField({name:'descriptionUa',title:'Case story (Ukrainian)',type:'text',rows:5}),
    defineField({name:'cover',title:'Cover image',type:'image',options:{hotspot:true},fields:[defineField({name:'alt',title:'Alt text',type:'string'})],validation:Rule=>Rule.required()}),
    defineField({name:'gallery',title:'Case gallery (optional)',type:'array',of:[{type:'image',options:{hotspot:true},fields:[{name:'alt',title:'Alt text',type:'string'},{name:'caption',title:'Caption',type:'string'}]}]}),
    defineField({name:'presentationImages',title:'Original case presentation exports, unchanged',description:'Upload long PNG/JPG slides exported from Figma. Site renders them edge-to-edge without cropping or reformatting.',type:'array',of:[{type:'image',options:{hotspot:false},fields:[{name:'alt',title:'Alt text',type:'string'}]}]}),
    defineField({name:'figmaFileKey',title:'Original Figma file key (optional)',type:'string',description:'Used for live Figma embeds when no exported presentation images are supplied.'}),
    defineField({name:'figmaFrames',title:'Original Figma frames (optional)',description:'Keep original width and height, without cropping.',type:'array',of:[{type:'object',fields:[defineField({name:'name',title:'Frame label',type:'string'}),defineField({name:'nodeId',title:'Figma node ID, e.g. 3843:5323',type:'string'}),defineField({name:'width',title:'Original width, px',type:'number'}),defineField({name:'height',title:'Original height, px',type:'number'})]}]}),
    defineField({name:'caseStudy',title:'On-site case study',type:'object',description:'Visible directly on this website; Behance is not required.',fields:[
      ...['tag','tagUa','statement','statementUa','ideaTitle','ideaTitleUa','solutionTitle','solutionTitleUa','closing','closingUa'].map(name=>defineField({name,title:name,type:'string'})),
      ...['intro','introUa','idea','ideaUa','solution','solutionUa'].map(name=>defineField({name,title:name,type:'text',rows:4})),
      defineField({name:'disciplines',title:'Disciplines',type:'array',of:[{type:'string'}]}),
      defineField({name:'typography',title:'Typography',type:'array',of:[{type:'string'}]}),
      defineField({name:'steps',title:'Design process stages',type:'array',of:[{type:'string'}]}),
      defineField({name:'colors',title:'Color palette',type:'array',of:[{type:'object',fields:[defineField({name:'name',title:'Name',type:'string'}),defineField({name:'hex',title:'HEX color',type:'string'})]}]}),
    ]}),
    defineField({name:'behanceUrl',title:'Optional Behance source link (not displayed on the site)',type:'url'}),
  ],
  preview:{select:{title:'title',subtitle:'type',media:'cover'}}
});
