const { exec } = require('child_process');
const util = require('util');

// Promisify exec function
const execPromise = util.promisify(exec);
const punctuateScriptPath = '../ml/punctuate.py';

async function punctuateText(inputString) {
    const command = `python ${punctuateScriptPath} "${inputString}"`;

    return execPromise(command)
        .then(({ stdout, stderr }) => {
            if (stderr) {
                throw new Error(`Command stderr: ${stderr}`);
            }
            return stdout.trim();
        });
}

// Example usage with then/catch
const inputString = "the atm protein is a single high molecular weight protein predominantly confined to the nucleus of human fibroblasts but is present in both nuclear and microsomal fractions from human lymphoblast cells and peripheral blood lymphocytes atm protein levels and localization remain constant throughout all stages of the cell cycle truncated atm protein was not detected in lymphoblasts from ataxia telangiectasia patients homozygous for mutations leading to premature protein termination exposure of normal human cells to gamma irradiation and the radiomimetic drug neocarzinostatin had no effect on atm protein levels in contrast to a noted rise in p53 levels over the same time interval these findings are consistent with a role for the atm protein in ensuring the fidelity of dna repair and cell cycle regulation following genome damage";
punctuateText(inputString)
    .then(result => {
        console.log(`Output: ${result}`);
    })
    .catch(error => {
        console.error(`Error: ${error.message}`);
    });