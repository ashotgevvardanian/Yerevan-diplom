/**
 * Three.js 3D Model Loader Boilerplate
 * This script initializes a 3D scene in the #three-container element.
 */

function initModel(modelId) {
    const container = document.getElementById('three-container');
    if (!container) return;

    // SCENE
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0a); // Dark background for contrast

    // CAMERA
    const camera = new THREE.PerspectiveCamera(45, container.offsetWidth / container.offsetHeight, 0.1, 1000);
    camera.position.set(5, 5, 5);

    // RENDERER
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.offsetWidth, container.offsetHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    container.innerHTML = ''; // Clear placeholder text
    container.appendChild(renderer.domElement);

    // LIGHTS
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 10, 7);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    // CONTROLS
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    // Load Model Placeholder (Box or Ground)
    const geometry = new THREE.BoxGeometry(2, 2, 2);
    const material = new THREE.MeshStandardMaterial({ 
        color: 0x0078d4, 
        roughness: 0.1, 
        metalness: 0.5 
    });
    const cube = new THREE.Mesh(geometry, material);
    cube.castShadow = true;
    cube.receiveShadow = true;
    scene.add(cube);

    // Add a Grid Helper
    const gridHelper = new THREE.GridHelper(10, 10, 0x555555, 0x222222);
    scene.add(gridHelper);

    // Loader for GLB
    const loader = new THREE.GLTFLoader();
    loader.load(`/static/models/${modelId}.glb`, (gltf) => {
        const model = gltf.scene;
        
        // Center the model
        const box = new THREE.Box3().setFromObject(model);
        const center = box.getCenter(new THREE.Vector3());
        model.position.sub(center);
        
        scene.remove(cube); // Remove placeholder cube
        scene.add(model);
        
        // Adjust camera to fit model
        const size = box.getSize(new THREE.Vector3());
        const maxDim = Math.max(size.x, size.y, size.z);
        camera.position.set(maxDim * 1.5, maxDim * 1.5, maxDim * 1.5);
        controls.target.set(0, 0, 0);
        controls.update();

        console.log(`Model ${modelId} loaded successfully`);
    }, undefined, (error) => {
        console.error('Error loading model:', error);
    });

    // ANIMATION LOOP
    function animate() {
        requestAnimationFrame(animate);
        
        // Auto-rotation for the placeholder cube
        cube.rotation.y += 0.005;
        cube.rotation.x += 0.002;
        
        controls.update();
        renderer.render(scene, camera);
    }

    animate();

    // HANDLE RESIZE
    window.addEventListener('resize', () => {
        camera.aspect = container.offsetWidth / container.offsetHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.offsetWidth, container.offsetHeight);
    });
}
