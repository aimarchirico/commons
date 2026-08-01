package no.chirico.commons.test

/**
 * Exercises [BaseArchitectureTest]'s own rules against this module, since the class is otherwise
 * only ever instantiated by consumers' own architecture tests and would never run here on its own.
 */
class BaseArchitectureTestTest : BaseArchitectureTest()
