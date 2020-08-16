# GraphGuard


GraphGuard is a tool originally created to update Hooks for Xposed Modules. It tries to match functions and classes in 
newer versions with updated Proguard Mappings by applying different strategies.

Androguard requires a lot of RAM and compute, and since we need both analyzed APKs in memory to work with them, this 
program is quite resource-intentsive. `htop` reports a 13gb RAM usage, though your mileage may vary.

Since this is so resource-intensive, all of it is packed into the [Jupyter Notebook](GraphGuard.ipynb). This makes it 
much more usable and interactive for the person working on it.

# Run it
* To run the notebook - Install Jupyter notebook (`pip install notebook`)
* Install dependencies:
  * Install Androguard (`pip install androguard`)

* Configure it for your project:
  * Replace the `file_paths` and change them to the target APKs.
  * Replace `named_c_decs`, `named_m_decs`, `named_f_decs` to customize which methods it will try to match. These can be
    generated with Akrolyb.
  * Replace `c_file`, `m_file`, `f_file` to the declaration files that you want to be updated automatically.

* Use the results
  * All matched declarations are printed.
  * If you use Akrolyb, declarations are extracted from the specified files and replaced automatically. Unmatched
    declarations are marked with `/* TODO */ ` comments in the generated files. Copy paste the results and only worry
    about the unmatched declarations.
  * GraphGuard can generate new, updated declarations. If you use Akrolyb, it is recommended to use its CodeGen for 
    GraphGuard instead  


# How it works

GraphGuard internally applies different "strategies" which generate candidates and submit them to the "Accumulator". If 
a strategy returns a single candidate, the accumulator will consider it an optimal match. For multiple candidates, it 
compares the candidates to the candidates of other strategies.


# Examples
I applied this to the "Instaprefs" project (private repository, created by [marzika](https://github.com/marzika)). It 
found about 82% (42/51) of the hooks going from version 143 to 150, so with a 7 version difference. I could not find any
errors in GraphGuard's results. I want it to fail rather than give false results, so I sticked mostly to exact 
conditions and matchings.
