use crate::bomb::TimerMode;
use crate::modules::ModuleNew;
use crate::prelude::*;
use itertools::Itertools;
use rand::prelude::*;
use serenity::model::prelude::*;
use serenity::prelude::*;
use serenity::utils::MessageBuilder;
use std::collections::HashSet;
use std::time::Duration;

const MAX_MODULES: u32 = 101;

fn ensure_no_bomb(ctx: &Context, msg: &Message) -> Result<(), ErrorMessage> {
    if crate::bomb::running_in(ctx, msg) {
        return Err((
            "Bomb already running".to_owned(),
            if msg.guild_id.is_some() {
                "A bomb is already running in this channel. Join in with the fun, run your own bomb by messaging the bot in private, or suggest detonating with `!detonate` (majority has to agree).".to_owned()
            } else {
                "A bomb is already running in this channel. If you don't want to defuse this bomb anymore, consider using `!detonate`.".to_owned()
            },
        ));
    }

    Ok(())
}

fn start_bomb(
    ctx: &Context,
    msg: &Message,
    timer: TimerMode,
    ruleseed: u32,
    modules: &[ModuleNew],
) {
    unimplemented!();
}

pub fn cmd_run(ctx: &Context, msg: &Message, params: Parameters<'_>) -> Result<(), ErrorMessage> {
    ensure_no_bomb(&ctx, &msg)?;

    let mut params = params.peekable();
    let mut named = Vec::new();

    while let Some(index) = params.peek().and_then(|param| param.find('=')) {
        let (name, value) = params.next().unwrap().split_at(index);
        named.push(get_named_parameter(name, value)?);
    }

    let named = consolidate_named_parameters(named.into_iter())?;

    use lazy_static::lazy_static;
    use regex::Regex;
    lazy_static! {
        static ref REGEX: Regex = Regex::new(r"(\w|[+-]) (\w|[+-])").unwrap();
    };

    let mut chosen_modules = vec![];

    let rng = &mut rand::thread_rng();
    for group in params
        .join(" ")
        .split(',')
        .map(str::trim)
        .filter(|param| !param.is_empty())
        .map(|param| REGEX.replace_all(param, "$1$2"))
    {
        let mut parts = group.split(' ');
        let specifier = parts.next().unwrap(); // always Some because we filter on is_empty
        let count = parts.next().ok_or_else(|| {
            (
                "Missing count".to_owned(),
                MessageBuilder::new()
                    .push("Please specify a count after ")
                    .push_mono_safe(specifier)
                    .build(),
            )
        })?;

        let count: u32 = match count.parse() {
            Ok(count) if count <= MAX_MODULES => count,
            Err(ref why) if why.kind() != &core::num::IntErrorKind::Overflow => {
                return Err((
                    "Syntax error".to_owned(),
                    MessageBuilder::new()
                        .push("Expected a count, found ")
                        .push_mono_safe(count)
                        .build(),
                ));
            }
            _ => {
                return Err((
                    "Count too large".to_owned(),
                    format!("I like your enthusiasm, but don't you think that's a bit too many modules? Could you limit yourself to {} for now?", MAX_MODULES),
                ));
            }
        };

        let each = match parts.next() {
            Some("each") => true,
            None => false,
            Some(other) => {
                return Err((
                    "Syntax error".to_owned(),
                    MessageBuilder::new()
                        .push("Expected `each` or a comma, found ")
                        .push_mono_safe(other)
                        .build(),
                ));
            }
        };

        if let Some(garbage) = parts.next() {
            return Err((
                "Trailing arguments".to_owned(),
                MessageBuilder::new()
                    .push("Expected a comma or message end, found ")
                    .push_mono_safe(garbage)
                    .build(),
            ));
        }

        let group_modules = parse_group(specifier)?;

        if group_modules.is_empty() {
            return Err((
                "Empty module set".to_owned(),
                MessageBuilder::new()
                    .push("The module group specifier ")
                    .push_mono_safe(specifier)
                    .push(" excludes all implemented modules.")
                    .build(),
            ));
        }

        if each {
            for _ in 0..count {
                chosen_modules.extend(group_modules.iter().map(|module| module.0));
            }
        } else {
            let group_modules: Vec<_> = group_modules.iter().map(|module| module.0).collect();

            for _ in 0..count {
                chosen_modules.push(*group_modules.choose(rng).unwrap());
            }
        }
    }

    Ok(())
}

// Work around rust-lang/rust#46989
#[derive(Clone, Copy)]
struct HashableModuleNew(ModuleNew);

impl PartialEq for HashableModuleNew {
    fn eq(&self, other: &HashableModuleNew) -> bool {
        self.0 as usize == other.0 as usize
    }
}

use std::fmt;
impl fmt::Debug for HashableModuleNew {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        (self.0 as usize).fmt(f)
    }
}

impl Eq for HashableModuleNew {}

use std::hash::{Hash, Hasher};
impl Hash for HashableModuleNew {
    fn hash<H: Hasher>(&self, state: &mut H) {
        (self.0 as usize).hash(state);
    }
}

fn specifier_no_meaning(
    input: &str,
    f: impl FnOnce(&mut MessageBuilder) -> &mut MessageBuilder,
) -> Result<!, ErrorMessage> {
    let mut builder = MessageBuilder::new();
    builder
        .push("The module group specifier ")
        .push_mono_safe(input);
    f(&mut builder);
    let msg = builder.push(". This has no defined meaning.").build();
    Err(("Syntax error".to_owned(), msg))
}

fn parse_group(input: &str) -> Result<HashSet<HashableModuleNew>, ErrorMessage> {
    let mut output = HashSet::new();

    let mut starting_index = 0;
    let mut removing = false;

    for (index, ch) in input.char_indices() {
        if ch == '+' || ch == '-' {
            let name = &input[starting_index..index];

            if name.is_empty() {
                specifier_no_meaning(input, |m| {
                    if index == 0 {
                        m.push(" starts with an operator")
                    } else {
                        m.push(
                            " contains two operators without a module or group between them, after ",
                        )
                        .push_mono_safe(&input[..index - 1])
                    }
                })?;
            }

            handle_group(&mut output, name, removing)?;

            starting_index = index + 1;
            removing = ch == '-';
        }
    }

    let name = &input[starting_index..];

    if name.is_empty() {
        specifier_no_meaning(input, |m| m.push(" ends with an operator"))?;
    }

    handle_group(&mut output, &input[starting_index..], removing)?;
    Ok(output)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_group_test() {
        assert_eq!(parse_group("thing"),
            Err((
                "No such module".to_owned(),
                "`thing` is not recognized as a module or module group name. Try **!modules** to get a list."
                .to_owned()
            ))
        );

        for valid_single in &[
            "wires",
            "wires+wires",
            "wires+wires+wires",
            "wires-wires+wires",
        ] {
            let result = parse_group(valid_single).unwrap();
            assert_eq!(result.len(), 1);
            assert_eq!(
                result.iter().next(),
                Some(&HashableModuleNew(crate::modules::wires::init))
            );
        }

        for valid_empty in &["wires-wires", "wires-all", "wires+wires-wires"] {
            let result = parse_group(valid_empty).unwrap();
            assert_eq!(result.len(), 0);
        }

        assert_eq!(parse_group("+"), Err((
            "Syntax error".to_owned(),
            "The module group specifier `+` starts with an operator. This has no defined meaning.".to_owned(),
        )));

        assert_eq!(parse_group("wires+"), Err((
            "Syntax error".to_owned(),
            "The module group specifier `wires+` ends with an operator. This has no defined meaning.".to_owned(),
        )));

        assert_eq!(parse_group("wires+-mods"), Err((
            "Syntax error".to_owned(),
            "The module group specifier `wires+-mods` contains two operators without a module or \
             group between them, after `wires`. This has no defined meaning.".to_owned(),
        )));
    }
}

fn handle_group(
    output: &mut HashSet<HashableModuleNew>,
    name: &str,
    removing: bool,
) -> Result<(), ErrorMessage> {
    match crate::modules::MODULE_GROUPS.get(name) {
        Some(&group) => {
            for &module in group {
                if removing {
                    output.remove(&HashableModuleNew(module));
                } else {
                    output.insert(HashableModuleNew(module));
                }
            }
        }
        // TODO: fuzzy suggestions
        None => return Err((
            "No such module".to_owned(),
            MessageBuilder::new()
            .push_mono_safe(name)
            .push(" is not recognized as a module or module group name. Try **!modules** to get a list.")
            .build())),
    }

    Ok(())
}

/// The value of a single named parameter.
enum NamedParameter {
    Ruleseed(u32),
    Timer(TimerMode),
}

/// A list of values for all named parameters
struct NamedParameters {
    ruleseed: u32,
    timer: Option<TimerMode>,
}

fn consolidate_named_parameters(
    params: impl Iterator<Item = NamedParameter>,
) -> Result<NamedParameters, ErrorMessage> {
    let mut ruleseed = None;
    let mut timer = None;

    for param in params {
        match param {
            NamedParameter::Ruleseed(seed) => {
                if ruleseed.replace(seed).is_some() {
                    return Err((
                        "Repeated parameter".to_owned(),
                        "It does not make sense to specify more than one rule seed.".to_owned(),
                    ));
                }
            }
            NamedParameter::Timer(specifier) => {
                if timer.replace(specifier).is_some() {
                    return Err((
                        "Repeated parameter".to_owned(),
                        "It does not make sense to specify more than one timer value.".to_owned(),
                    ));
                }
            }
        }
    }

    Ok(NamedParameters {
        ruleseed: ruleseed.unwrap_or(ktane_utils::random::VANILLA_SEED),
        timer,
    })
}

fn get_named_parameter(name: &str, value: &str) -> Result<NamedParameter, ErrorMessage> {
    match name {
        "ruleseed" | "seed" | "rules" => {
            use ktane_utils::random::MAX_VALUE;
            match value.parse() {
                Ok(seed) => {
                    if seed <= MAX_VALUE {
                        Ok(NamedParameter::Ruleseed(seed))
                    } else {
                        Err((
                            "Seed too large".to_owned(),
                            format!(
                                "Please limit yourself to seeds not larger than {}",
                                MAX_VALUE
                            ),
                        ))
                    }
                }
                Err(_) => Err((
                    "Couldn't parse argument".to_owned(),
                    MessageBuilder::new()
                        .push_mono_safe(value)
                        .push(" is not a valid rule seed. Try using a natural number.")
                        .build(),
                )),
            }
        }
        "timer" => {
            if let Ok(mode) = value.parse() {
                Ok(NamedParameter::Timer(mode))
            } else if let Ok(time) = humantime::parse_duration(value) {
                Ok(NamedParameter::Timer(TimerMode::Normal(time)))
            } else {
                Err(("Not a valid timer value".to_owned(),
                MessageBuilder::new()
                    .push_mono_safe(value)
                    .push(" is not a valid argument for `timer`. Try *zen*, *time*, a duration such as `8m30s` or omit the argument.")
                    .build()))
            }
        }
        _ => Err((
            "Unknown parameter".to_owned(),
            MessageBuilder::new()
                .push_mono_safe(value)
                .push(
                    " is not a valid argument name. Try *timer* or *ruleseed* \
                     (alias *seed* or *rules*).",
                )
                .build(),
        )),
    }
}
