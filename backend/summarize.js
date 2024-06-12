const { exec } = require('child_process');
const util = require('util');

const execPromise = util.promisify(exec);

async function executePythonScript(scriptPath, inputString) {
    // Escape double quotes inside the JSON string
    const escapedInputString = inputString.replace(/"/g, '\\"');
    const command = `python ${scriptPath} "${escapedInputString}"`;

    return execPromise(command)
      .then(({ stdout, stderr }) => {
        if (stderr) {
            throw new Error(`Command stderr: ${stderr}`);
        }
        return stdout.trim();
      });
}

const pythonScriptPath = '../ml/sum_testing.py';
const sentences = [
    "The Solar System consists of the Sun and all the objects that are gravitationally bound to it.",
    "These objects include the eight planets and their moons, dwarf planets, and countless smaller bodies such as asteroids and comets.",
    "The Sun, a G-type main-sequence star, is at the center of the Solar System and contains over 99% of its total mass.",
    "The four inner planets, Mercury, Venus, Earth, and Mars, are terrestrial planets, composed mostly of rock and metal.",
    "The four outer planets, Jupiter, Saturn, Uranus, and Neptune, are gas giants, with thick atmospheres composed primarily of hydrogen and helium.",
    "The Solar System formed about 4.6 billion years ago from the gravitational collapse of a giant molecular cloud.",
    "Apart from planets, the Solar System also contains regions such as the asteroid belt, Kuiper belt, and the Oort cloud, which are populated by various small celestial bodies.",
    "Earth, the third planet from the Sun, is the only known planet to support life.",
    "The Solar System's location in the Milky Way galaxy is in the Orion Arm, about 27,000 light-years from the galactic center.",
    "Exploration of the Solar System has been conducted by robotic spacecraft, with missions providing valuable data about its composition and dynamics."
];

executePythonScript(pythonScriptPath, JSON.stringify(sentences))
    .then(summary => { console.log(summary); })
    .catch(error => { console.error(error); });
