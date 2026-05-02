<%*
const IDX = Object.freeze({"depth":0, "text":1, "parent":2, "size":3, "children": 4, "objectId":5});

//check if an editor is the active view
const editor = this.app.workspace.activeLeaf?.view?.editor;
if(!editor) return;

//initialize the tree with the title of the document as the first element
let tree = [[0,this.app.workspace.activeLeaf?.view?.getDisplayText(),-1,0,[],0]];
const linecount = editor.lineCount();

//helper function, use regex to calculate indentation depth, and to get line text
function getLineProps (i) {
  props = editor.getLine(i).match(/^(\t*)-\s+(.*)/);
  return [props[1].length+1, props[2]];
}

//a vector that will hold last valid parent for each depth
let parents = [0];

//load outline into tree
for(i=0;i<linecount;i++) {
  [depth,text] = getLineProps(i);
  if(depth>parents.length) parents.push(i+1);
  else parents[depth] = i+1;
  tree.push([depth,text,parents[depth-1],1,[]]);
  tree[parents[depth-1]][IDX.children].push(i+1);
}

//recursive function to crawl the tree and identify height aka. size of each node
function crawlTree(i) {
  if(i>linecount) return 0;
  size = 0;
  if((i+1<=linecount && tree[i+1][IDX.depth] <= tree[i][IDX.depth])|| i == linecount) { //I am a leaf
    tree[i][IDX.size] = 1; 
    return 1; 
  }
  tree[i][IDX.children].forEach((node)=>{ 
    size += crawlTree(node);
  });
  tree[i][IDX.size] = size; 
  return size;   
}

crawlTree(0);

//Build the mindmap in Excalidraw
const width = 300;
const height = 100;
const ea = ExcalidrawAutomate;
ea.reset();

//stores position offset of branch/leaf in height units
offsets = [0];

for(i=0;i<=linecount;i++) {
  depth = tree[i][IDX.depth];
  if (depth == 1) ea.style.strokeColor = '#'+(Math.random()*0xFFFFFF<<0).toString(16);
  tree[i][IDX.objectId] = ea.addText(depth*width,((tree[i][IDX.size]/2)+offsets[depth])*height,tree[i][IDX.text],{box:true});  
  //set child offset equal to parent offset
  if((depth+1)>offsets.length) offsets.push(offsets[depth]);
  else offsets[depth+1] = offsets[depth];
  offsets[depth] += tree[i][IDX.size];
  if(tree[i][IDX.parent]!=-1) {
    ea.connectObjects(tree[tree[i][IDX.parent]][IDX.objectId],"right",tree[i][IDX.objectId],"left",{startArrowHead: 'dot'});
  }
}

await ea.create({onNewPane: true});
%>