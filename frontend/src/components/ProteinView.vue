<script setup lang="ts">

import { ref, onMounted } from 'vue'

import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { XRButton } from 'three/examples/jsm/webxr/XRButton.js';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import { XRControllerModelFactory } from 'three/examples/jsm/webxr/XRControllerModelFactory.js';
import { PerspectiveCamera,
         Scene,
         WebGLRenderer,
         Group,
         Raycaster,
         Object3D,
         Matrix4,
         Vector3,
         Quaternion,
         Color,
         Mesh,
         HemisphereLight,
         DirectionalLight,
         MeshStandardMaterial,
         BufferGeometry,
         Line
 } from 'three';

import oneak4_1 from '../assets/models/1ak4_1.obj'
import oneak4_2 from '../assets/models/1ak4_2.obj'

const socket = new WebSocket(import.meta.env.VITE_BACKEND_WEBSOCKET_URL?import.meta.env.VITE_BACKEND_WEBSOCKET_URL:"ws://localhost:8888");

const container = ref<HTMLDivElement>()
const renderCanvas = ref<HTMLCanvasElement>()
const plotRoot = ref<HTMLDivElement>()

let camera : PerspectiveCamera, scene: Scene, renderer: WebGLRenderer;
let controller1 : Group, controller2 : Group;
let controllerGrip1, controllerGrip2;

let raycaster : Raycaster;

const intersected = new Array<Object3D>;
const tempMatrix = new Matrix4();

let controls : OrbitControls, group : Group;
let score;

onMounted(()=>{
  console.log(import.meta.env)
  init();
  renderer.setAnimationLoop( render );
})

function send_data(name : string, position : Vector3, direction : Vector3) {
  let message = {
    chain: name,
    pos: position,
    dir: direction
  };
  socket.send(JSON.stringify(message))
}

function init() {
  scene = new Scene();
  scene.background = new Color( 0x808080 );
  scene.updateMatrixWorld(true);

  camera = new PerspectiveCamera( 50, window.innerWidth / window.innerHeight, 0.1, 10 );
  camera.position.set( 0, 1.6, 3 );

  controls = new OrbitControls( camera, renderCanvas.value as HTMLCanvasElement );
  controls.target.set( 0, 1.6, 0 );
  controls.update();

  //const floorGeometry = new THREE.PlaneGeometry( 4, 4 );
  // const floorMaterial = new THREE.MeshStandardMaterial( {
  //   color: 0xeeeeee,
  //   roughness: 1.0,
  //   metalness: 0.0
  // } );
  // const floor = new Mesh( floorGeometry, floorMaterial );
  // floor.rotation.x = - Math.PI / 2;
  // floor.position.y = -1
  // floor.receiveShadow = true;
  // scene.add( floor );

  scene.add( new HemisphereLight( 0x808080, 0x606060 ) );

  const light = new DirectionalLight( 0xffffff );
  light.position.set( 0, 6, 0 );
  light.castShadow = true;
  light.shadow.camera.top = 2;
  light.shadow.camera.bottom = - 2;
  light.shadow.camera.right = 2;
  light.shadow.camera.left = - 2;
  light.shadow.mapSize.set( 4096, 4096 );
  scene.add( light );

  group = new Group();
  scene.add( group );


  // instantiate a loader
  const loader1 = new OBJLoader();
  loader1.load(
    oneak4_1,
    function ( object : Object3D ) {
      let baseColor = Math.random() * 0xffffff

      const material = new MeshStandardMaterial( {
        color: baseColor,
        roughness: 0.7,
        metalness: 0.0
      } );
      object.traverse( function( child ) {
        if ( child instanceof Mesh ) {
          child.scale.setScalar( 0.5 );
          child.material = material;
          child.castShadow = true;
          child.receiveShadow = true;
          child.name = 'chain1';
          child.position.y = 1.6;
          child.position.z = -2.0;
          child.userData['baseColor'] = baseColor
        }
      });

      object.traverse( function(child) {
        if ( child instanceof Mesh ) {
          group.add(child)
          }
        } 
      );
    },
    // called when loading is in progresses
    function ( xhr : any ) { console.log( ( xhr.loaded / xhr.total * 100 ) + '% loaded' );},
    // called when loading has errors
    function () {console.log( 'An error happened' );}
  );

  // instantiate a loader
  const loader2 = new OBJLoader();
  loader2.load(
    oneak4_2,
    function ( object : Object3D ) {
      const material = new MeshStandardMaterial( {
        color: Math.random() * 0xffffff,
        roughness: 0.7,
        metalness: 0.0
      } );
      object.traverse( function( child ) {
        if ( child instanceof Mesh ) {
          child.scale.setScalar( 0.5 );
          child.material = material;
          child.castShadow = true;
          child.receiveShadow = true;
          child.name = 'chain2';
                          child.position.y = 1.6;
                          child.position.z = -2.0;
          }
        } 
      );

      object.traverse( function(child) {
        if ( child instanceof Mesh ) {
          group.add(child)
          }
        } 
      );
    },
    // called when loading is in progresses
    function ( xhr : any ) { console.log( ( xhr.loaded / xhr.total * 100 ) + '% loaded' );},
    // called when loading has errors
    function () {console.log( 'An error happened' );}
  );

  //

  renderer = new WebGLRenderer( { antialias: true, canvas: renderCanvas.value } );
  renderer.setPixelRatio( window.devicePixelRatio );
  renderer.setSize( window.innerWidth, window.innerHeight );
  renderer.shadowMap.enabled = true;
  renderer.xr.enabled = true;

  plotRoot.value?.appendChild( XRButton.createButton( renderer ) );

  // controllers
  controller1 = renderer.xr.getController( 0 );
  controller1.addEventListener( 'selectstart', onSelectStart );
  controller1.addEventListener( 'selectend', onSelectEnd );
  scene.add( controller1 );

  controller2 = renderer.xr.getController( 1 );
  controller2.addEventListener( 'selectstart', onSelectStart );
  controller2.addEventListener( 'selectend', onSelectEnd );
  scene.add( controller2 );

  const controllerModelFactory = new XRControllerModelFactory();

  controllerGrip1 = renderer.xr.getControllerGrip( 0 );
  controllerGrip1.add( controllerModelFactory.createControllerModel( controllerGrip1 ) );
  scene.add( controllerGrip1 );

  controllerGrip2 = renderer.xr.getControllerGrip( 1 );
  controllerGrip2.add( controllerModelFactory.createControllerModel( controllerGrip2 ) );
  scene.add( controllerGrip2 );

  // listen to backend
  socket.addEventListener('message', 
    function (event) {
      //const time = new Date().getTime();
      const parsedData = JSON.parse(event.data);
      const eventType = parsedData.type;

      if (eventType === 'score') {

        score = parsedData.data;
        let name = parsedData.name;
        let obj = group.children.find((obj)=>obj.userData.name == name) as Mesh
        (obj.material as MeshStandardMaterial).color.r = 1;
        (obj.material as MeshStandardMaterial).color.g = score/10;
        (obj.material as MeshStandardMaterial).color.b = score/10;
      }
    }
  )

  const geometry = new BufferGeometry().setFromPoints( [ new Vector3( 0, 0, 0 ), new Vector3( 0, 0, - 1 ) ] );

  const line = new Line( geometry );
  line.name = 'line';
  line.scale.z = 5;

  controller1.add( line.clone() );
  controller2.add( line.clone() );

  raycaster = new Raycaster();

  //

  window.addEventListener( 'resize', onWindowResize );

}

function onWindowResize() {

  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();

  renderer.setSize( window.innerWidth, window.innerHeight );

}

function onSelectStart( event : any ) {

  const controller = event.target;

  const intersections = getIntersections( controller );

  if ( intersections.length > 0 ) {

    const intersection = intersections[ 0 ];

    const object = intersection.object as Mesh;
    (object.material as MeshStandardMaterial).emissive.b = 1;
    controller.attach( object );
    
    controller.userData.selected = object;

    var position = new Vector3();
    controller.userData.selected.getWorldPosition(position);
    console.log(position.x + ',' + position.y + ',' + position.z);

  }

}

function onSelectEnd( event : any ) {

  const controller = event.target;

  if ( controller.userData.selected !== undefined ) {

    const object = controller.userData.selected;
    object.material.emissive.b = 0;
    group.attach( object );

    controller.userData.selected = undefined;


  }


}

function getIntersections( controller : Group ) {

  tempMatrix.identity().extractRotation( controller.matrixWorld );

  raycaster.ray.origin.setFromMatrixPosition( controller.matrixWorld );
  raycaster.ray.direction.set( 0, 0, - 1 ).applyMatrix4( tempMatrix );

  return raycaster.intersectObjects( group.children, false );

}

function intersectObjects( controller : Group ) {

  // Do not highlight when already selected

  if ( controller.userData.selected !== undefined ) {
    
    var position = new Vector3();
    controller.userData.selected.getWorldPosition(position);
    
    var quaternion = new Quaternion();
    controller.userData.selected.getWorldQuaternion(quaternion);

    var direction = new Vector3();
    controller.userData.selected.getWorldDirection(direction);
    
    let name = controller.userData.selected.name
    send_data(name, position, direction)
    return
  };

  const line = controller.getObjectByName( 'line' );
  const intersections = getIntersections( controller );

  if(line){
    if ( intersections.length > 0 ) {

      const intersection = intersections[ 0 ];

      const object = intersection.object as Mesh;
      (object.material as MeshStandardMaterial).emissive.r = 1;
      intersected.push( object );

      line.scale.z = intersection.distance;

    } else {

      line.scale.z = 5;

    }
  }

}

function cleanIntersected() {

  while ( intersected.length ) {

    const object = intersected.pop() as Mesh;
    (object.material as MeshStandardMaterial).emissive.r = 0;

  }

}

function render() {

  cleanIntersected();

  intersectObjects( controller1 );
  intersectObjects( controller2 );

  renderer.render( scene, camera );

}
</script>

<template>
  <div ref="plotRoot" class="h-100 w-100 rounded">
    <div ref='container' class="d-flex justify-content-center align-items-center flex-column w-100 h-100">
      <canvas ref='renderCanvas' class="rounded" style="background: none;"/>
    </div>
  </div>
</template>

<style scoped>

</style>
